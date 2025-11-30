import logging
import sys

from fastapi import FastAPI

from app.core import register_exception_handlers
from app.db.database import Base, engine
from app.api import api_router
from app import models

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 데이터베이스 테이블 생성
# 모든 모델 클래스 검사 + 존재하지 않는 테이블 생성
def init_db():
    """데이터베이스 테이블 초기화"""
    Base.metadata.create_all(bind=engine)

# 애플리케이션 생성
app = FastAPI(
    title="HCI Fashion Recommendation API",
    description="Fashion Recommendation Application for HCI Lecture",
    version="1.0.0"
)

# 커스텀 예외 핸들러 등록
register_exception_handlers(app)

# API 라우터 등록
app.include_router(api_router, prefix="/api")

# 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {"message": "HCI Fashion Recommendation API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

