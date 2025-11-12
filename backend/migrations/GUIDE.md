## 🧭 Alembic 사용 가이드

FastAPI + SQLAlchemy 프로젝트에서 Alembic으로 스키마 변경을 관리하는 방법입니다.

### 1. 의존성 설치
```bash
pip install alembic
pip install psycopg2-binary  # PostgreSQL 드라이버가 없다면 추가
pip freeze | grep alembic    # 설치 확인
```

### 2. 초기 설정
```bash
alembic init migrations
```
명령을 실행하면 `alembic.ini`와 `migrations/` 디렉터리가 생성됩니다.

### 3. `env.py` 편집
Alembic이 프로젝트의 모델을 인식할 수 있도록 `migrations/env.py`를 수정합니다.

**필수 추가 블록**
```1:13:backend/migrations/env.py
from logging.config import fileConfig
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db.database import Base, DATABASE_URL
from app.models import *
```

**메타데이터와 DB URL 연결**
```28:29:backend/migrations/env.py
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

### 4. 리비전 생성
```bash
alembic revision --autogenerate -m "add timezone-aware timestamps"
```
자동 생성된 스크립트는 반드시 열어 보고 `upgrade()`/`downgrade()` 내용이 의도한 대로 나왔는지 확인하세요. 변경 사항이 없으면 함수가 `pass`로 남습니다.

### 5. DB에 적용
```bash
alembic upgrade head
```
특정 리비전으로 이동하려면 `alembic upgrade <revision_id>`를 사용합니다.

### 6. 주의사항
- 자동 생성된 리비전에서 불필요한 `drop_table` 등의 파괴적 명령이 들어갔는지 항상 검토합니다.
- 기존에 수동으로 만든 스키마를 Alembic으로 전환할 때는 빈 리비전으로 `alembic stamp head`를 먼저 실행해 현재 상태를 베이스라인으로 맞춘 뒤 사용하세요.
- 운영 DB URL을 사용하는 경우, 적용 전에 `env.py`에서 `DATABASE_URL`이 정확한지 확인하세요.
- `migrations/__pycache__/`나 `migrations/versions/*.pyc` 같은 임시 파일은 `.gitignore`에 추가해 Git에 올리지 않습니다.