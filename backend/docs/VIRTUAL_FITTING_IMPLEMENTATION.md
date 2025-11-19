# 가상 피팅 구현 문서

## 개요

가상 피팅 기능은 사용자가 업로드한 사진에 선택한 아이템들을 순차적으로 입혀서 최종 결과 이미지를 생성하고, 그 결과에 대한 LLM 추천 메시지를 생성하는 기능입니다.

## 구현 흐름

### 1. API 엔드포인트

**POST /api/virtual-fitting**

- 사용자가 가상 피팅 작업을 시작합니다.
- 요청: `userPhotoUrl`, `items` (최소 1개, 최대 3개)
- 응답: `jobId`, `status="processing"`, `createdAt` (202 Accepted)
- 비동기 처리: 백그라운드에서 실제 피팅 작업 수행

### 2. 검증 단계 (`start_virtual_fitting()`)

1. 사용자 사진 존재 확인 (`UserImage` 테이블)
2. 아이템 개수 검증 (1~3개)
3. 카테고리 중복 확인 (각 카테고리당 최대 1개)
4. 카테고리 유효성 확인 (top, bottom, outer)
5. 아이템 ID 유효성 확인 (`Item` 테이블)
6. `FittingResult` 레코드 생성 (status="processing")
7. `FittingResultItem` 레코드 생성

### 3. 순차적 피팅 처리 (`_process_virtual_fitting_async()`)

#### 3.1 이미지 다운로드
- 사용자 사진 다운로드 (`userPhotoUrl`)
- 각 아이템 이미지 다운로드 (`items[].imageUrl`)
- 캔버스 생성 (사용자 이미지 크기 기준)

#### 3.2 순차적 피팅 호출

**기존 구조 (제거됨):**
```
person + [garment1, garment2, garment3] + canvas → 최종 이미지
```

**새로운 구조:**
```
1단계: person + garment1 + canvas → result_image_1
2단계: result_image_1 + garment2 + canvas → result_image_2 (있으면)
3단계: result_image_2 + garment3 + canvas → final_image (있으면)
```

**구현 세부사항:**
- 각 단계마다 `_generate_fitting_image_single_step_sync()` 호출
- 동일한 프롬프트 사용 (단일 garment용으로 수정)
- 각 단계마다 `current_step` 업데이트 (item.category 기반)
- 각 단계마다 DB 커밋 (진행 상황 저장)
- 실패 시 `failed_step`에 해당 카테고리 저장

#### 3.3 LLM 메시지 생성

최종 이미지로 LLM 추천 메시지 생성:
- `_generate_llm_message_sync()` 호출
- 프롬프트: "이 가상 피팅 결과 이미지를 보고 사용자에게 친근하고 매력적인 추천 메시지를 작성해주세요. 한 문장으로, 이모지를 포함하여 작성해주세요. (최대 50자)"
- `FittingResult.llm_message`에 저장

#### 3.4 결과 저장

- 최종 이미지 파일 저장 (`aiofiles` 사용)
- `FittingResultImage` 레코드 생성
- `FittingResult.status = "completed"` 업데이트

## 비동기 처리 구조

### 백그라운드 작업 흐름

```
FastAPI 엔드포인트
  ↓
BackgroundTasks.add_task()
  ↓
_process_virtual_fitting_with_new_session() (동기 함수)
  ↓
asyncio.run(_process_virtual_fitting_async()) (비동기 함수)
  ↓
순차적 피팅 처리
  ├─ await _download_image() (비동기)
  ├─ await asyncio.to_thread(_generate_fitting_image_single_step_sync) (별도 스레드)
  ├─ await asyncio.to_thread(_generate_llm_message_sync) (별도 스레드)
  └─ await aiofiles.open().write() (비동기)
```

### 스레드 구조

1. **메인 이벤트 루프 스레드**
   - FastAPI 요청 처리
   - 비동기 작업 실행 (`await _download_image()`, `await aiofiles`)

2. **별도 스레드 (ThreadPoolExecutor)**
   - `asyncio.to_thread()`로 실행
   - Gemini API 호출 (동기 함수)
   - 메인 스레드를 블로킹하지 않음

### 타임아웃 설정

- **전체 피팅 작업**: 300초 (5분)
- **LLM 메시지 생성**: 15초
- 각 단계는 전체 타임아웃 내에서 실행

## 상태 관리

### FittingResult 상태 필드

- `status`: "processing" → "completed" / "failed" / "timeout"
- `current_step`: 현재 처리 중인 카테고리 (top/bottom/outer)
- `failed_step`: 실패한 단계의 카테고리
- `llm_message`: LLM 추천 메시지
- `finished_at`: 작업 완료/실패 시점

### 상태 전환

```
생성 → processing (current_step=top)
  ↓
processing (current_step=bottom)
  ↓
processing (current_step=outer)
  ↓
completed (current_step=None, llm_message=생성됨)
```

## 에러 처리

### 검증 에러 (400 Bad Request)

- `PhotoRequiredError`: 사용자 사진 없음
- `InsufficientItemsError`: 아이템 1개 미만
- `TooManyItemsError`: 아이템 3개 초과 또는 카테고리당 1개 초과
- `DuplicateCategoryError`: 동일 카테고리 중복
- `InvalidCategoryError`: 유효하지 않은 카테고리
- `InvalidItemIdError`: 존재하지 않는 아이템 ID

### 처리 중 에러

- **이미지 다운로드 실패**: Exception 발생 → status="failed"
- **피팅 단계 실패**: `failed_step` 저장 → status="failed"
- **타임아웃**: status="timeout"
- **LLM 메시지 생성 실패**: 메시지는 None이지만 작업은 완료

## 주요 논의사항 및 결정사항

### 1. 순차적 호출 구조

**결정**: 모든 아이템을 한번에 전달하는 대신, 순차적으로 호출

**이유**:
- 더 정확한 피팅 결과
- 각 단계별 진행 상황 추적 가능
- 실패 지점 명확히 파악 가능

**구현**:
- `_generate_fitting_image_single_step_sync()`: 단일 garment 피팅
- 각 단계의 결과 이미지를 다음 단계의 입력으로 사용

### 2. 비동기 처리 방식

**결정**: FastAPI `BackgroundTasks` 사용

**이유**:
- 간단한 구현
- 별도 인프라 불필요 (Celery 등)
- 202 Accepted 응답으로 즉시 반환

**구현**:
- `BackgroundTasks.add_task()`로 백그라운드 작업 등록
- 새로운 DB 세션 생성 (`SessionLocal()`)
- `asyncio.run()`으로 비동기 함수 실행

### 3. Gemini API 호출 방식

**결정**: 동기 함수를 `asyncio.to_thread()`로 실행

**이유**:
- `google.genai.Client`는 동기 API만 제공
- 메인 이벤트 루프를 블로킹하지 않기 위해 별도 스레드에서 실행

**구현**:
- `_generate_fitting_image_single_step_sync()`: 동기 함수
- `_generate_llm_message_sync()`: 동기 함수
- `asyncio.to_thread()`로 별도 스레드에서 실행

### 4. LLM 메시지 생성

**결정**: 최종 이미지만 전달하여 메시지 생성

**이유**:
- 이미지만으로 충분한 정보 제공 가능
- 사용자/아이템 정보는 이미지에서 파악 가능

**구현**:
- `_generate_llm_message_sync()`: 최종 이미지 + 프롬프트
- `llm_service.py` 패턴 참고
- 실패 시 None 반환 (작업은 계속 진행)

### 5. 상태 추적

**결정**: `current_step`으로 진행 상황 추적

**이유**:
- 사용자가 현재 어떤 단계를 처리 중인지 확인 가능
- 디버깅 및 모니터링 용이

**구현**:
- 각 단계마다 `fitting_result.current_step = item.category` 업데이트
- 완료 시 `current_step = None`으로 초기화

### 6. 파일 저장

**결정**: `aiofiles` 사용하여 비동기 파일 저장

**이유**:
- 비동기 컨텍스트에서 블로킹 방지
- `users_service.py`와 일관성 유지

**구현**:
- `async with aiofiles.open(file_path, "wb") as f:`
- `await f.write(final_image_bytes)`

### 7. 타임아웃 설정

**결정**: 전체 작업에 대한 타임아웃 적용

**이유**:
- 각 단계별 타임아웃보다 전체 타임아웃이 더 명확
- 사용자 경험 개선

**구현**:
- 피팅 작업: 300초 (5분)
- LLM 메시지: 15초

## 파일 구조

```
backend/app/
├── api/
│   └── virtual_fitting.py          # API 엔드포인트
├── services/
│   └── virtual_fitting_service.py  # 비즈니스 로직
├── schemas/
│   ├── user_request.py             # VirtualFittingRequest, FittingItemRequest
│   └── user_response.py             # VirtualFittingResponse
├── core/
│   └── exceptions.py                # 가상 피팅 관련 예외
└── models/
    ├── fitting_result.py            # FittingResult 모델
    ├── fitting_result_item.py       # FittingResultItem 모델
    └── fitting_result_image.py     # FittingResultImage 모델
```

## 참고 파일

- `test2.py`: Gemini 이미지 편집 파이프라인 참고
- `llm_service.py`: LLM 메시지 생성 패턴 참고
- `users_service.py`: 파일 저장 패턴 참고

## 향후 개선 사항

1. **모델 변경**: 환경변수로 모델 선택 가능하도록 개선
2. **프롬프트 최적화**: 피팅 품질 향상을 위한 프롬프트 개선
3. **캐싱**: 동일한 조합의 피팅 결과 캐싱 고려
4. **진행률 추적**: WebSocket 등을 통한 실시간 진행률 전송
5. **재시도 로직**: 실패 시 자동 재시도 기능

