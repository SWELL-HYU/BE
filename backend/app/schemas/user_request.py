"""
사용자 관련 요청 스키마 정의.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, EmailStr, Field


class UserGender(str, Enum):
    male = "male"
    female = "female"


# 사용자 회원가입 요청 스키마
class UserCreateRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)
    name: str = Field(min_length=2, max_length=50)
    gender: UserGender


# 사용자 로그인 요청 스키마
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)


# 사용자 선호도 설정 요청 스키마
class UserPreferencesRequest(BaseModel):
    hashtag_ids: List[int] = Field(alias="hashtagIds")
    sample_outfit_ids: List[int] = Field(alias="sampleOutfitIds")

    class Config:
        populate_by_name = True

