"""
사용자 관련 응답 스키마 정의.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user_request import UserGender


class UserPayload(BaseModel):
    id: int = Field(alias="id")
    email: EmailStr
    name: str
    gender: Optional[UserGender] = None
    profile_image_url: Optional[str] = Field(
        default=None,
        alias="profileImageUrl",
    )
    created_at: datetime = Field(alias="createdAt")

    class Config:
        # populate_by_name=True: 내부 snake_case 필드명을 그대로 사용하면서, JSON 직렬화 시 alias(camelCase)를 출력 가능하도록 설정.
        # orm_mode=True: SQLAlchemy ORM 객체를 직접 Pydantic 모델로 변환할 수 있게 허용.
        populate_by_name = True
        orm_mode = True


class UserResponseData(BaseModel):
    user: UserPayload
    token: str


class UserResponse(BaseModel):
    success: bool = True
    data: UserResponseData


