"""
사용자 관련 요청 스키마 정의.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserGender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


# 사용자 회원가입 요청 스키마
class UserCreateRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)
    name: str = Field(min_length=2, max_length=50)
    gender: Optional[UserGender] = None
    preferred_tags: Optional[str] = Field(
        default=None, # 선호 태그가 없을 경우 None
        description="콤마(,)로 구분된 선호 태그 문자열",
    )


# 사용자 로그인 요청 스키마
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)

