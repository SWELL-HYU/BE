# HCI Fashion Recommendation Backend

FastAPI 기반 추천 시스템 백엔드.

## 📋 사전 요구사항
- **Python 3.11(필수!)**
- **pip** / **venv**
- **Docker & Docker Compose** (PostgreSQL 컨테이너용)

## 🚀 로컬 개발 환경 설정

```bash
cd backend

# 1) 가상환경 생성 및 활성화(if use Mac brew: /opt/homebrew/bin/python3.11 -m venv .venv) 
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

## 🗄 PostgreSQL 컨테이너 실행

```bash
docker-compose up -d          # DB만 실행

# 종료 시
docker-compose down
```

## ▶️ 애플리케이션 실행

```bash
# 가상환경이 활성화된 상태에서
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- **API**: http://localhost:8000  
- **API 문서**: http://localhost:8000/docs  
- **PostgreSQL**: localhost:5432

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── db/              # DB 설정 (database.py)
│   ├── models/          # SQLAlchemy 모델
│   ├── routers/         # API 라우터
│   ├── schemas/         # Pydantic 스키마
│   ├── crud/            # CRUD 작업
│   └── services/        # 비즈니스 로직
├── main.py              # FastAPI 진입점
├── requirements.txt     # 의존성 목록
├── docker-compose.yml   # PostgreSQL 전용 컴포즈
```
