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

## 🧭 Alembic 사용 가이드

1. **의존성 설치**
   ```bash
   pip install alembic
   pip install psycopg2-binary  # PostgreSQL 드라이버가 없다면 추가
   pip freeze | grep alembic    # 설치 확인
   ```

2. **초기 시작 명령어**
   ```bash
   alembic init migrations
   ```
   `alembic.ini`와 `migrations/` 디렉터리가 생성됩니다.

3. **`env.py` 수정**
   - 모듈 경로 추가 및 Base, DB URL 로드  
     ```python
```1:13:backend/migrations/env.py
from logging.config import fileConfig
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.database import Base, DATABASE_URL
from app.models import *
```
   - 메타데이터와 DB URL 주입  
     ```python
```28:29:backend/migrations/env.py
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

4. **리비전 생성**
   ```bash
   alembic revision --autogenerate -m "add timezone-aware timestamps"
   ```
   생성된 스크립트의 `upgrade()`/`downgrade()` 내용을 반드시 검토하세요.

5. **마이그레이션 적용**
   ```bash
   alembic upgrade head
   ```
   특정 버전으로 이동하려면 `alembic upgrade <revision_id>`를 사용할 수 있습니다.

6. **주의사항**
   - 생성된 리비전 파일을 커밋하기 전에 불필요한 `drop_table` 등 파괴적인 명령이 없는지 확인합니다.
   - 이미 스키마가 있는 DB에 Alembic을 도입할 때는 빈 리비전으로 `alembic stamp head`를 수행해 베이스라인을 맞춘 뒤 사용하세요.
   - 운영 DB URL을 사용하는 경우 `env.py`의 `DATABASE_URL`이 정확한지 재검토 후 `alembic upgrade head`를 실행하세요.
   - `migrations/__pycache__/`나 `versions/*.pyc` 등은 Git에 포함하지 않습니다 (`.gitignore` 참고).
