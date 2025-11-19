"""
사용자 관련 응답 스키마 정의.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from app.schemas.recommendation_response import PaginationPayload
from app.schemas.user_request import UserGender


class PreferredTagPayload(BaseModel):
    """선호 태그 페이로드."""
    id: int
    name: str


class HashtagOptionPayload(BaseModel):
    """해시태그 옵션 페이로드."""
    id: int
    name: str


class SampleOutfitOptionPayload(BaseModel):
    """예시 코디 옵션 페이로드."""
    id: int
    image_url: str = Field(alias="imageUrl")
    style: Optional[str] = None
    season: Optional[str] = None

    class Config:
        populate_by_name = True


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

# 선호도 설정 옵션 응답 데이터 스키마 1
class PreferencesOptionsResponseData(BaseModel):
    hashtags: List[HashtagOptionPayload]
    sample_outfits: List[SampleOutfitOptionPayload] = Field(alias="sampleOutfits")

    class Config:
        populate_by_name = True

# 선호도 설정 옵션 응답 데이터 스키마 2
class PreferencesOptionsResponse(BaseModel):
    success: bool = True
    data: PreferencesOptionsResponseData


# 선호도 설정 응답 데이터 스키마 1
class PreferencesResponseUser(BaseModel):
    """선호도 설정 응답의 사용자 정보."""
    id: int
    has_completed_onboarding: bool = Field(alias="hasCompletedOnboarding")

    class Config:
        populate_by_name = True


# 선호도 설정 응답 데이터 스키마 2
class PreferencesResponseData(BaseModel):
    message: str
    user: PreferencesResponseUser


# 선호도 설정 응답 데이터 스키마 3
class PreferencesResponse(BaseModel):
    success: bool = True
    data: PreferencesResponseData


# 프로필 사진 업로드 응답 데이터 스키마 1
class ProfilePhotoUploadResponseData(BaseModel):
    """프로필 사진 업로드 응답 데이터."""
    photo_url: str = Field(alias="photoUrl")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


# 프로필 사진 업로드 응답 데이터 스키마 2
class ProfilePhotoUploadResponse(BaseModel):
    success: bool = True
    data: ProfilePhotoUploadResponseData


# 프로필 사진 삭제 응답 데이터 스키마 1
class ProfilePhotoDeleteResponseData(BaseModel):
    """프로필 사진 삭제 응답 데이터."""
    message: str
    deleted_at: datetime = Field(alias="deletedAt")

    class Config:
        populate_by_name = True


# 프로필 사진 삭제 응답 데이터 스키마 2
class ProfilePhotoDeleteResponse(BaseModel):
    success: bool = True
    data: ProfilePhotoDeleteResponseData


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


# 옷장에 아이템 저장 응답 데이터 스키마 1
class SaveClosetItemResponseData(BaseModel):
    message: str
    saved_at: datetime = Field(alias="savedAt")

    class Config:
        populate_by_name = True


# 옷장에 아이템 저장 응답 데이터 스키마 2
class SaveClosetItemResponse(BaseModel):
    success: bool = True
    data: SaveClosetItemResponseData


# 옷장에서 아이템 삭제 응답 데이터 스키마 1
class DeleteClosetItemResponseData(BaseModel):
    message: str
    deleted_at: datetime = Field(alias="deletedAt")

    class Config:
        populate_by_name = True


# 옷장에서 아이템 삭제 응답 데이터 스키마 2
class DeleteClosetItemResponse(BaseModel):
    success: bool = True
    data: DeleteClosetItemResponseData


# 옷장 아이템 페이로드
class ClosetItemPayload(BaseModel):
    id: int
    category: str
    brand: Optional[str] = None
    name: str
    price: Optional[int] = None
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    purchase_url: Optional[str] = Field(default=None, alias="purchaseUrl")
    saved_at: datetime = Field(alias="savedAt")

    class Config:
        populate_by_name = True


# 카테고리별 개수 페이로드
class CategoryCountsPayload(BaseModel):
    top: int
    bottom: int
    outer: int

    class Config:
        populate_by_name = True


# 옷장 아이템 목록 조회 응답 데이터 스키마 1
class ClosetItemsResponseData(BaseModel):
    items: List[ClosetItemPayload]
    pagination: PaginationPayload
    category_counts: CategoryCountsPayload = Field(alias="categoryCounts")

    class Config:
        populate_by_name = True


# 옷장 아이템 목록 조회 응답 데이터 스키마 2
class ClosetItemsResponse(BaseModel):
    success: bool = True
    data: ClosetItemsResponseData


# 가상 피팅 시작 응답 데이터 스키마 1
class VirtualFittingResponseData(BaseModel):
    job_id: int = Field(alias="jobId", description="피팅 작업 고유 ID")
    status: str = Field(description="피팅 작업 상태")
    created_at: datetime = Field(alias="createdAt", description="피팅 작업 생성 일시")

    class Config:
        populate_by_name = True


# 가상 피팅 시작 응답 데이터 스키마 2
class VirtualFittingResponse(BaseModel):
    success: bool = True
    data: VirtualFittingResponseData


# 가상 피팅 상태 조회 - Processing 상태 페이로드
class VirtualFittingJobStatusProcessingPayload(BaseModel):
    job_id: int = Field(alias="jobId", description="피팅 작업 고유 ID")
    status: str = Field(default="processing", description="피팅 작업 상태")
    current_step: str = Field(alias="currentStep", description="현재 처리 단계")

    class Config:
        populate_by_name = True


# 가상 피팅 상태 조회 - Completed 상태 페이로드
class VirtualFittingJobStatusCompletedPayload(BaseModel):
    job_id: int = Field(alias="jobId", description="피팅 작업 고유 ID")
    status: str = Field(default="completed", description="피팅 작업 상태")
    result_image_url: str = Field(alias="resultImageUrl", description="피팅 결과 이미지 URL")
    llm_message: Optional[str] = Field(alias="llmMessage", default=None, description="LLM 평가 메시지")
    completed_at: datetime = Field(alias="completedAt", description="작업 완료 일시")
    processing_time: int = Field(alias="processingTime", description="처리 시간 (초)")

    class Config:
        populate_by_name = True


# 가상 피팅 상태 조회 - Failed 상태 페이로드
class VirtualFittingJobStatusFailedPayload(BaseModel):
    job_id: int = Field(alias="jobId", description="피팅 작업 고유 ID")
    status: str = Field(default="failed", description="피팅 작업 상태")
    error: str = Field(description="에러 메시지")
    failed_step: str = Field(alias="failedStep", description="실패한 단계")
    failed_at: datetime = Field(alias="failedAt", description="작업 실패 일시")

    class Config:
        populate_by_name = True


# 가상 피팅 상태 조회 - Timeout 상태 페이로드
class VirtualFittingJobStatusTimeoutPayload(BaseModel):
    job_id: int = Field(alias="jobId", description="피팅 작업 고유 ID")
    status: str = Field(default="timeout", description="피팅 작업 상태")
    error: str = Field(description="에러 메시지")
    timeout_at: datetime = Field(alias="timeoutAt", description="타임아웃 발생 일시")

    class Config:
        populate_by_name = True


# 가상 피팅 상태 조회 - Union 타입
VirtualFittingJobStatusPayload = Union[
    VirtualFittingJobStatusProcessingPayload,
    VirtualFittingJobStatusCompletedPayload,
    VirtualFittingJobStatusFailedPayload,
    VirtualFittingJobStatusTimeoutPayload,
]


# 가상 피팅 상태 조회 응답 스키마
class VirtualFittingJobStatusResponse(BaseModel):
    success: bool = True
    data: VirtualFittingJobStatusPayload


# 가상 피팅 이력 조회 - 아이템 페이로드
class FittingHistoryItemPayload(BaseModel):
    item_id: int = Field(alias="itemId", description="아이템 고유 ID")
    category: str = Field(description="카테고리")
    name: str = Field(description="상품명")

    class Config:
        populate_by_name = True


# 가상 피팅 이력 조회 - 피팅 페이로드
class FittingHistoryPayload(BaseModel):
    job_id: int = Field(alias="jobId", description="가상 피팅 작업 고유 ID")
    status: str = Field(description="작업 상태")
    result_image_url: Optional[str] = Field(
        alias="resultImageUrl",
        default=None,
        description="결과 이미지 URL (완료된 경우만)",
    )
    items: List[FittingHistoryItemPayload] = Field(description="피팅에 사용된 아이템 목록")
    created_at: datetime = Field(alias="createdAt", description="피팅 작업 생성 일시")

    class Config:
        populate_by_name = True


# 가상 피팅 이력 조회 - 응답 데이터
class FittingHistoryResponseData(BaseModel):
    fittings: List[FittingHistoryPayload] = Field(description="가상 피팅 이력 목록")
    pagination: PaginationPayload = Field(description="페이지네이션 정보")


# 가상 피팅 이력 조회 응답 스키마
class FittingHistoryResponse(BaseModel):
    success: bool = True
    data: FittingHistoryResponseData


# 가상 피팅 이력 삭제 응답 데이터 스키마 1
class DeleteFittingHistoryResponseData(BaseModel):
    message: str
    deleted_at: datetime = Field(alias="deletedAt")

    class Config:
        populate_by_name = True


# 가상 피팅 이력 삭제 응답 데이터 스키마 2
class DeleteFittingHistoryResponse(BaseModel):
    success: bool = True
    data: DeleteFittingHistoryResponseData


