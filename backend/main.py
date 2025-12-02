import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import register_exception_handlers
from app.db.database import Base, engine
from app.api import api_router
from app import models

# 환경 변수 로드
load_dotenv()

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

# CORS 미들웨어 설정
# TODO: 배포 시 고려
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

