"""
사용자 관련 응답 스키마 정의.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user_request import UserGender


class PreferredTagPayload(BaseModel):
    """선호 태그 페이로드."""
    id: int
    name: str


class PreferredCoordiPayload(BaseModel):
    """선호 코디 페이로드."""
    id: int
    style: Optional[str] = None
    season: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    main_image_url: Optional[str] = Field(
        default=None,
        alias="mainImageUrl",
    )
    preferred_at: datetime = Field(alias="preferredAt")

    class Config:
        populate_by_name = True


class UserPayload(BaseModel):
    id: int = Field(alias="id")
    email: EmailStr
    name: str
    gender: Optional[UserGender] = None
    profile_image_url: Optional[str] = Field(
        default=None,
        alias="profileImageUrl",
    )
    preferred_tags: Optional[List[PreferredTagPayload]] = Field(
        default=None,
        alias="preferredTags",
    )
    preferred_coordis: Optional[List[PreferredCoordiPayload]] = Field(
        default=None,
        alias="preferredCoordis",
    )
    has_completed_onboarding: bool = Field(alias="hasCompletedOnboarding")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        # populate_by_name=True: 내부 snake_case 필드명을 그대로 사용하면서, JSON 직렬화 시 alias(camelCase)를 출력 가능하도록 설정.
        # orm_mode=True: SQLAlchemy ORM 객체를 직접 Pydantic 모델로 변환할 수 있게 허용.
        populate_by_name = True
        orm_mode = True

# 회원가입 응답 데이터 스키마 1
class SignupResponseData(BaseModel):
    user: UserPayload

# 회원가입 응답 데이터 스키마 2
class SignupResponse(BaseModel):
    success: bool = True
    data: SignupResponseData

# 로그인 응답 데이터 스키마 1
class LoginResponseData(BaseModel):
    user: UserPayload
    token: str

# 로그인 응답 데이터 스키마 2
class LoginResponse(BaseModel):
    success: bool = True
    data: LoginResponseData

# 로그아웃 응답 데이터 스키마
class LogoutResponse(BaseModel):
    success: bool = True
    message: str = "로그아웃되었습니다"

# 내 정보 조회 응답 데이터 스키마 1
class MeResponseData(BaseModel):
    user: UserPayload

# 내 정보 조회 응답 데이터 스키마 2
class MeResponse(BaseModel):
    success: bool = True
    data: MeResponseData


