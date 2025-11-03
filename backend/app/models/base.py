from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.db.database import Base


class BaseModel(Base):
    """
    모든 모델의 기본 클래스
    공통 필드를 포함
    """
    __abstract__ = True # 이 클래스는 table 생성에 사용되지 않는다.
    
    id = Column(Integer, primary_key=True, index=True) # 기본 키
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # 생성 시간
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) # 수정 시간

