"""
코디 관련 스키마 정의.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# 본 코디 스킵 기록 요청 스키마
class SkipOutfitsRequest(BaseModel):
    outfit_ids: List[int] = Field(alias="outfitIds", min_length=1, description="스킵할 코디 ID 리스트")

    class Config:
        populate_by_name = True


# 본 코디 스킵 기록 응답 데이터 스키마 1
class SkipOutfitsResponseData(BaseModel):
    message: str
    recorded_count: int = Field(alias="recordedCount")
    skipped_count: int = Field(alias="skippedCount")

    class Config:
        populate_by_name = True


# 본 코디 스킵 기록 응답 데이터 스키마 2
class SkipOutfitsResponse(BaseModel):
    success: bool = True
    data: SkipOutfitsResponseData


# 코디 좋아요 추가 응답 데이터 스키마 1
class AddFavoriteResponseData(BaseModel):
    outfit_id: int = Field(alias="outfitId")
    is_favorited: bool = Field(alias="isFavorited")
    favorited_at: datetime = Field(alias="favoritedAt")

    class Config:
        populate_by_name = True


# 코디 좋아요 추가 응답 데이터 스키마 2
class AddFavoriteResponse(BaseModel):
    success: bool = True
    data: AddFavoriteResponseData


# 코디 좋아요 취소 응답 데이터 스키마 1
class RemoveFavoriteResponseData(BaseModel):
    outfit_id: int = Field(alias="outfitId")
    is_favorited: bool = Field(alias="isFavorited")
    unfavorited_at: datetime = Field(alias="unfavoritedAt")

    class Config:
        populate_by_name = True


# 코디 좋아요 취소 응답 데이터 스키마 2
class RemoveFavoriteResponse(BaseModel):
    success: bool = True
    data: RemoveFavoriteResponseData

