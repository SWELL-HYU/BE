"""
사용자 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Header, status, UploadFile
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, extract_bearer_token
from app.db.database import get_db
from app.schemas.users import (
    PreferencesOptionsResponse,
    PreferencesOptionsResponseData,
    PreferencesResponse,
    PreferencesResponseData,
    PreferencesResponseUser,
    ProfilePhotoDeleteResponse,
    ProfilePhotoDeleteResponseData,
    ProfilePhotoUploadResponse,
    ProfilePhotoUploadResponseData,
    UserPreferencesRequest,
)
from app.services.auth_service import get_user_from_token
from app.services.users_service import (
    delete_profile_photo,
    get_preferences_options_data,
    set_user_preferences,
    upload_profile_photo,
)

# 사용자 관련 라우터(접두사: /users)
router = APIRouter(prefix="/users", tags=["Users"])


# 사용자 선호도 설정 옵션 제공 API
@router.get(
    "/preferences/options",
    status_code=status.HTTP_200_OK,
    response_model=PreferencesOptionsResponse,
)
def get_preferences_options(
    authorization: str = Header(...),  # 인증 헤더
    db: Session = Depends(get_db),
) -> PreferencesOptionsResponse:
    """사용자 선호도 설정 옵션 제공 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)

    # 선호도 설정 옵션 데이터 조회 (사용자 성별에 따라 필터링)
    hashtags, sample_outfits = get_preferences_options_data(db, user.gender)

    # 응답 반환
    return PreferencesOptionsResponse(
        data=PreferencesOptionsResponseData(
            hashtags=hashtags,
            sampleOutfits=sample_outfits,
        )
    )


# 사용자 선호도 설정 API
@router.post(
    "/preferences",
    status_code=status.HTTP_200_OK,
    response_model=PreferencesResponse,
)
def set_preferences(
    payload: UserPreferencesRequest,
    authorization: str = Header(...),  # 인증 헤더
    db: Session = Depends(get_db),
) -> PreferencesResponse:
    """사용자 선호도 설정 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)

    # 선호도 설정
    updated_user = set_user_preferences(db, user.user_id, payload)

    # 응답 반환
    return PreferencesResponse(
        data=PreferencesResponseData(
            message="선호도가 저장되었습니다",
            user=PreferencesResponseUser(
                id=updated_user.user_id,
                hasCompletedOnboarding=updated_user.has_completed_onboarding,
            ),
        )
    )


# 프로필 사진 업로드 API
@router.post(
    "/profile-photo",
    status_code=status.HTTP_200_OK,
    response_model=ProfilePhotoUploadResponse,
)
async def upload_profile_photo_endpoint(
    photo: UploadFile = File(...), # 프로필 사진 파일
    authorization: str = Header(...),  # 인증 헤더
    db: Session = Depends(get_db),
) -> ProfilePhotoUploadResponse:
    """프로필 사진 업로드 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)

    # 프로필 사진 업로드
    user_image = await upload_profile_photo(db, user.user_id, photo)

    # 응답 반환
    return ProfilePhotoUploadResponse(
        data=ProfilePhotoUploadResponseData(
            photoUrl=user_image.image_url,
            createdAt=user_image.created_at,
        )
    )


# 프로필 사진 삭제 API
@router.delete(
    "/profile-photo",
    status_code=status.HTTP_200_OK,
    response_model=ProfilePhotoDeleteResponse,
)
async def delete_profile_photo_endpoint(
    authorization: str = Header(...),  # 인증 헤더
    db: Session = Depends(get_db),
) -> ProfilePhotoDeleteResponse:
    """프로필 사진 삭제 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)

    # 프로필 사진 삭제
    deleted_at, had_photo = await delete_profile_photo(db, user.user_id)

    # 응답 메시지 결정
    message = "사진이 삭제되었습니다" if had_photo else "삭제할 사진이 없습니다"

    # 응답 반환
    return ProfilePhotoDeleteResponse(
        data=ProfilePhotoDeleteResponseData(
            message=message,
            deletedAt=deleted_at,
        )
    )

