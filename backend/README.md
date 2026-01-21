# HCI Fashion Recommendation Backend

FastAPI 기반 추천 시스템 백엔드.

## 📋 사전 요구사항
- **Python 3.11(필수!)**
- **pip** / **venv**
- **Docker & Docker Compose** (PostgreSQL 컨테이너용)

## 🚀 로컬 개발 환경 설정

```bash
cd backend

# 1) 가상환경 생성 및 활성화(if use Mac brew: /opt/homebrew/bin/python3.11 -m venv .venv -> python3.11기반을 사용하기 위해) 
python -m venv .venv    
source .venv/bin/activate    # Windows: .venv\Scripts\activate
                            

# 2) 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 3) 환경 변수 설정 (.env)
cp .env.example .env          # 파일이 없다면 직접 생성
```

`.env` 파일(또는 쉘 환경 변수)에 아래 값을 지정하세요.

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hci_fashion_db
```

## 🗄 PostgreSQL 컨테이너 실행(로컬 개발시)

```bash
docker-compose up -d          # DB만 실행

# 종료 시
docker-compose down
```

## ▶️ 애플리케이션 실행

```bash
# 가상환경이 활성화된 상태에서
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 또는 (개발용)
fastapi run
```

- **API**: http://localhost:8000  
- **API 문서**: http://localhost:8000/docs  
- **PostgreSQL**: localhost:5432

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/             # API 라우터 (기능별 분리)
│   │   ├── auth.py      # 인증 (회원가입, 로그인, 로그아웃)
│   │   ├── users.py     # 사용자 (프로필, 선호도 설정)
│   │   ├── items.py     # 아이템 상세 조회
│   │   ├── recommendations.py  # 개인화 추천 코디
│   │   ├── outfits.py   # 코디 목록 조회, 좋아요, 스킵
│   │   ├── closet.py    # 옷장 (아이템 저장/조회/삭제)
│   │   └── virtual_fitting.py  # 가상 피팅
│   ├── core/            # 핵심 설정 및 유틸리티
│   │   ├── exceptions.py    # 커스텀 예외 처리
│   │   ├── security.py      # JWT 인증/인가
│   │   └── file_utils.py    # 파일 업로드 유틸리티
│   ├── db/              # DB 설정
│   │   └── database.py  # 데이터베이스 연결
│   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── user.py, coordi.py, item.py 등
│   ├── schemas/         # Pydantic 스키마 (기능별 분리)
│   │   ├── common.py    # 공통 스키마 (PaginationPayload)
│   │   ├── auth.py      # 인증 관련
│   │   ├── users.py     # 사용자 관련
│   │   ├── items.py     # 아이템 관련
│   │   ├── outfits.py   # 코디 관련
│   │   ├── closet.py    # 옷장 관련
│   │   ├── virtual_fitting.py  # 가상 피팅 관련
│   │   └── recommendation_response.py  # 추천 응답
│   ├── services/        # 비즈니스 로직 (기능별 분리)
│   │   ├── auth_service.py
│   │   ├── users_service.py
│   │   ├── item_service.py
│   │   ├── recommendations_service.py
│   │   ├── outfits_service.py
│   │   ├── closet_service.py
│   │   ├── virtual_fitting_service.py
│   │   └── llm_service.py  # LLM (Gemini) 통합
├── data/                # 초기 데이터 (JSON)
│   ├── final_data_complete1.json
│   └── tags_sample.json
├── docs/                # 문서
│   ├── API_TEST.md      # Postman 테스트 가이드
│   ├── CACHING_STRATEGY.md
│   ├── LLM_IMPLEMENTATION.md
│   └── VIRTUAL_FITTING_IMPLEMENTATION.md
├── migrations/          # Alembic 마이그레이션
├── scripts/             # 데이터 로딩 스크립트
│   ├── load_coordis.py
│   └── load_tags.py
├── uploads/             # 업로드된 파일
│   ├── users/           # 사용자 프로필 사진
│   └── fitting/         # 가상 피팅 결과 이미지
├── main.py              # FastAPI 진입점
├── requirements.txt     # 의존성 목록
└── docker-compose.yml   # PostgreSQL 컨테이너 설정
```

### 실행 명렁어
추가로 t3.large랑 25gb 스토리지 볼륨 권장
```
#!/bin/bash
# --- 1. 시스템 업데이트 ---
dnf update -y
# --- 2. 필수 개발 도구 및 라이브러리 설치 (딱 이것만!) ---
# - python3.11: 실행 환경
# - postgresql15-devel: DB 드라이버 빌드용
# - mesa-libGL, glib2: AI/이미지 처리용 (OpenCV 등)
# - git: 코드 다운로드용
# - gcc: 라이브러리 컴파일용
dnf install -y python3.11 python3.11-devel python3.11-pip \
    git gcc \
    postgresql15-devel \
    mesa-libGL glib2
# --- 3. 완료 메시지 ---
echo "Ready to Deploy!" > /home/ec2-user/setup_complete.txt
```