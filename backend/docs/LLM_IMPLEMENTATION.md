# LLM 메시지 생성 구현 가이드

이 문서는 개인화 추천 코디 조회 API에서 사용되는 LLM 메시지 생성 기능의 구현 방식을 설명합니다.

## 목차

1. [개요](#개요)
2. [아키텍처](#아키텍처)
3. [구현 세부사항](#구현-세부사항)
4. [비동기 처리 전략](#비동기-처리-전략)
5. [주요 고려사항](#주요-고려사항)
6. [성능 최적화](#성능-최적화)

---

## 개요

### 목적

각 추천 코디에 대해 사용자에게 친근하고 매력적인 개인화된 추천 메시지를 생성합니다.

### 기술 스택

- **LLM API**: Google Gemini 2.5 Flash
- **비동기 HTTP 클라이언트**: `httpx`
- **비동기 처리**: `asyncio`
- **동시성 제어**: `asyncio.Semaphore`

---

## 아키텍처

### 전체 흐름

```
GET /api/recommendations 요청
  ↓
1. 추천 코디 ID 조회 (임시 함수)
  ↓
2. 코디 상세 정보 조회 (selectinload로 N+1 방지)
  ↓
3. 사용자 정보 조회
  ↓
4. LLM 메시지 생성 (병렬 처리)
   ├─ 각 코디별로 generate_llm_message() 호출
   ├─ Semaphore로 최대 10개 동시 요청 제한
   ├─ 이미지 다운로드 (httpx.AsyncClient)
   └─ Gemini API 호출 (asyncio.to_thread)
  ↓
5. 페이로드 생성 및 응답 반환
```

### 파일 구조

```
backend/app/services/
├── llm_service.py              # LLM 메시지 생성 로직
└── recommendations_service.py  # 추천 코디 조회 및 LLM 통합
```

---

## 구현 세부사항

### 1. LLM 서비스 (`llm_service.py`)

#### 환경 변수 설정

```python
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
TIMEOUT_SECONDS = 10.0  # 타임아웃 설정 (초)
```

**주의**: 환경 변수 이름이 `GOOGLE_API_KEY`입니다. `.env` 파일에 설정해야 합니다.

#### `generate_llm_message()` 함수

**역할**: 코디와 사용자 정보를 받아 개인화된 LLM 메시지를 생성합니다.

**처리 단계**:

1. **API Key 확인**
   ```python
   if not GEMINI_API_KEY:
       return None  # API Key가 없으면 즉시 None 반환
   ```

2. **코디 이미지 URL 추출**
   - 메인 이미지 우선 (`is_main=True`)
   - 없으면 첫 번째 이미지 사용
   - SQLAlchemy relationship 접근은 **비동기 함수 내에서** 수행 (세션이 유효한 상태)

3. **이미지 다운로드 (비동기)**
   ```python
   async with httpx.AsyncClient(timeout=5.0) as client:
       image_response = await client.get(image_url)
       image_bytes = image_response.content
   ```
   - 실패 시 `None` 유지 (텍스트만 전달)

4. **프롬프트 구성**
   - 코디 정보 (스타일, 계절, 설명)
   - 사용자 정보 (이름, 성별)
   - 메시지 형식 요구사항 (한 문장, 이모지 포함, 최대 50자)

5. **Gemini API 호출**
   - `asyncio.to_thread()`로 동기 함수를 별도 스레드에서 실행
   - 타임아웃: 10초
   - 실패 시 `None` 반환

#### `_generate_sync()` 함수

**역할**: 동기 방식으로 Gemini API를 호출합니다.

**처리 단계**:

1. **Gemini API 클라이언트 생성**
   ```python
   client = Client(api_key=GEMINI_API_KEY)
   ```

2. **콘텐츠 구성**
   - 텍스트 프롬프트
   - 이미지가 있으면 `types.Part.from_bytes()`로 이미지 파트 추가

3. **API 호출 및 응답 처리**
   ```python
   response = client.models.generate_content(
       model=GEMINI_MODEL,
       contents=contents,
   )
   return response.text.strip()
   ```

**중요**: 이 함수는 `asyncio.to_thread()`로 호출되므로, SQLAlchemy 세션 접근을 하지 않도록 주의해야 합니다. 모든 필요한 데이터는 함수 호출 전에 추출되어 파라미터로 전달됩니다.

---

### 2. 추천 서비스 (`recommendations_service.py`)

#### LLM 메시지 생성 통합

```python
# 6. 코디별 LLM 메시지 생성 (병렬, Semaphore로 동시 요청 제한)
semaphore = asyncio.Semaphore(10)  # 최대 10개 동시 요청

async def generate_with_limit(coordi: Coordi) -> tuple[int, Optional[str]]:
    async with semaphore:
        message = await generate_llm_message(coordi, user)
        return coordi.coordi_id, message

tasks = [generate_with_limit(coordi) for coordi in coordis]
llm_results = await asyncio.gather(*tasks, return_exceptions=True)

# 코디 ID별 LLM 메시지 매핑
llm_messages = {}
for result in llm_results:
    if isinstance(result, Exception):
        continue
    coordi_id, message = result
    llm_messages[coordi_id] = message
```

**처리 흐름**:

1. **Semaphore 생성**: 최대 10개 동시 요청 제한
2. **Task 생성**: 각 코디에 대해 `generate_with_limit()` Task 생성
3. **병렬 실행**: `asyncio.gather()`로 모든 Task 병렬 실행
4. **결과 매핑**: `{coordi_id: message}` 딕셔너리로 변환

---

## 비동기 처리 전략

### 1. 이미지 다운로드

**문제**: 이미지 URL에서 이미지를 다운로드해야 함

**해결**: `httpx.AsyncClient` 사용
```python
async with httpx.AsyncClient(timeout=5.0) as client:
    image_response = await client.get(image_url)
    image_bytes = image_response.content
```

### 2. Gemini API 호출

**문제**: `google.genai.Client`는 동기 방식

**해결**: `asyncio.to_thread()`로 별도 스레드에서 실행
```python
result = await asyncio.wait_for(
    asyncio.to_thread(_generate_sync, prompt, image_bytes, mime_type),
    timeout=TIMEOUT_SECONDS,
)
```

**이유**: 
- 동기 함수를 비동기 컨텍스트에서 실행하면 이벤트 루프가 블로킹됨
- 별도 스레드에서 실행하면 다른 비동기 작업이 계속 진행 가능

### 3. SQLAlchemy 세션 접근

**문제**: `_generate_sync()`는 별도 스레드에서 실행되므로 SQLAlchemy 세션 접근 불가

**해결**: 필요한 데이터를 함수 호출 전에 추출하여 파라미터로 전달
```python
# ✅ 올바른 방식
image_url = main_image.image_url  # 세션이 유효한 상태에서 추출
image_bytes = await download_image(image_url)  # 비동기 다운로드
result = await asyncio.to_thread(_generate_sync, prompt, image_bytes, mime_type)

# ❌ 잘못된 방식
result = await asyncio.to_thread(_generate_sync, coordi, user)  # coordi.images 접근 불가
```

### 4. 병렬 처리 및 동시성 제어

**문제**: 여러 코디에 대해 LLM 메시지를 생성해야 함

**해결**: 
- `asyncio.gather()`로 병렬 실행
- `asyncio.Semaphore(10)`로 동시 요청 수 제한 (Rate Limit 방지)

**예시**:
```
20개 코디, 각 LLM 호출 2초 소요
- Semaphore 없음: 20개 × 2초 = 40초
- Semaphore=10: 최대 10개 동시 → 약 4초 (2초 × 2라운드)
```

---

## 주요 고려사항

### 1. API Key 확인

**현재 동작**:
- `GEMINI_API_KEY`가 없으면 즉시 `None` 반환
- LLM API 호출이 전혀 실행되지 않음
- 응답 시간이 매우 짧음 (38ms 수준)

**확인 방법**:
```bash
echo $GOOGLE_API_KEY
# 또는 .env 파일 확인
```

### 2. 타임아웃 처리

- **이미지 다운로드**: 5초
- **LLM API 호출**: 10초
- 타임아웃 발생 시 `None` 반환 (예외 발생하지 않음)

### 3. 예외 처리

**원칙**: 모든 예외를 무시하고 `None` 반환

- 이미지 다운로드 실패 → 텍스트만 전달
- LLM API 호출 실패 → `None` 반환
- 타임아웃 → `None` 반환

**이유**: LLM 메시지는 부가 기능이므로, 실패해도 전체 응답은 정상 반환

### 4. 순서 유지

**문제**: `asyncio.gather()`는 Task 생성 순서대로 결과를 반환하지만, 코디 ID 순서와 일치해야 함

**해결**: `coordi_id`를 함께 반환하여 매핑
```python
async def generate_with_limit(coordi: Coordi) -> tuple[int, Optional[str]]:
    message = await generate_llm_message(coordi, user)
    return coordi.coordi_id, message  # ID와 함께 반환

llm_messages = {}
for result in llm_results:
    coordi_id, message = result
    llm_messages[coordi_id] = message  # ID로 매핑
```

### 5. 추천 순서 유지

**문제**: `Coordi` 객체를 DB에서 조회할 때 `in_()` 쿼리는 순서를 보장하지 않음

**해결**: 추천 모델이 반환한 `coordi_ids` 순서대로 재정렬
```python
coordi_dict = {coordi.coordi_id: coordi for coordi in coordis}
coordis = [coordi_dict[cid] for cid in coordi_ids if cid in coordi_dict]
```

---

## 성능 최적화

### 1. N+1 쿼리 방지

**문제**: 각 코디의 이미지와 아이템을 조회할 때 N+1 쿼리 발생

**해결**: `selectinload` 사용
```python
coordis = db.execute(
    select(Coordi)
    .where(Coordi.coordi_id.in_(coordi_ids))
    .options(
        selectinload(Coordi.images),
        selectinload(Coordi.coordi_items).selectinload(CoordiItem.item).selectinload(Item.images),
    )
).scalars().all()
```

### 2. 병렬 처리

- **LLM 메시지 생성**: 모든 코디에 대해 병렬 실행
- **Semaphore 제한**: 최대 10개 동시 요청 (Rate Limit 방지)

### 3. 이미지 다운로드 최적화

- **비동기 HTTP 클라이언트**: `httpx.AsyncClient` 사용
- **타임아웃 설정**: 5초로 제한하여 무한 대기 방지
- **실패 처리**: 실패해도 텍스트만 전달하여 계속 진행

### 4. 응답 시간

**현재 동작**:
- `GEMINI_API_KEY` 없음: ~38ms (LLM 호출 안 함)
- `GEMINI_API_KEY` 있음: LLM 호출 시간에 따라 증가 (각 호출당 2-5초)

**최적화 방안** (향후):
- LLM 메시지 캐싱 (동일 코디에 대해 재사용)
  - Redis를 사용하여 동일 코디 ID에 대한 LLM 메시지를 캐싱
  - 캐시 키: `llm_message:{coordi_id}:{user_id}` 또는 `llm_message:{coordi_id}` (사용자 무관)
  - TTL 설정: 예) 24시간
- 부분 응답 (먼저 응답하고 LLM 메시지는 나중에 업데이트)
- 타임아웃 단축 (3초로 제한)

---

## 테스트 및 디버깅

### 로그 확인

현재는 로그가 없으므로, 디버깅 시 다음을 확인:

1. **환경 변수 확인**
   ```bash
   echo $GOOGLE_API_KEY
   ```

2. **응답 시간 확인**
   - 38ms 수준: API Key 없음 또는 LLM 호출 안 함
   - 2-5초 이상: LLM 호출 정상 실행

3. **응답 내용 확인**
   - `llmMessage` 필드가 `null`: LLM 호출 실패 또는 API Key 없음
   - `llmMessage` 필드에 값: LLM 호출 성공

### 향후 개선 사항

1. **로깅 추가**
   - LLM 호출 시작/완료 로그
   - 타임아웃/예외 로그
   - 성능 메트릭 (응답 시간)

2. **모니터링**
   - LLM 호출 성공률
   - 평균 응답 시간
   - 타임아웃 발생 빈도

---

## 참고 자료

- [Google Gemini API 문서](https://ai.google.dev/docs)
- [httpx 문서](https://www.python-httpx.org/)
- [asyncio 문서](https://docs.python.org/3/library/asyncio.html)

