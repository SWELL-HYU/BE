import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hci_fashion_db"
)

# Engine 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 연결 상태 확인
    echo=True  # 개발 환경에서 SQL 쿼리 로깅
)

# SessionLocal 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

def get_db():
    """
    데이터베이스 세션 의존성 주입
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

