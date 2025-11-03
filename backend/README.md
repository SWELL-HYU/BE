# HCI Fashion Recommendation Backend

FastAPI + PostgreSQL + Docker

## 📋 사전 요구사항

- **Docker** & **Docker Compose** 설치 필요
  - [Docker Desktop 다운로드](https://www.docker.com/products/docker-desktop)
  - 설치 확인: `docker --version`, `docker-compose --version`

## 🚀 빠른 시작

```bash
cd backend

# 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 중지
docker-compose down
```

### 접속

- **API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── db/          # DB 설정 (database.py)
│   ├── models/      # SQLAlchemy 모델 (base.py)
│   ├── routers/     # API 라우터
│   ├── schemas/     # Pydantic 스키마
│   ├── crud/        # CRUD 작업
│   └── services/    # 비즈니스 로직
├── main.py          # FastAPI 진입점
├── requirements.txt # 의존성
├── Dockerfile       # 컨테이너 설정
└── docker-compose.yml
```

## 📝 주요 명령어

```bash
# 로그 확인
docker-compose logs -f web

# DB 접속
docker-compose exec db psql -U postgres -d hci_fashion_db
```

