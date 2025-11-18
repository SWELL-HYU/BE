"""
인증 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token, extract_bearer_token
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_request import UserCreateRequest, UserLoginRequest
from app.schemas.user_response import (
    LoginResponse,
    LoginResponseData,
    LogoutResponse,
    MeResponse,
    MeResponseData,
    PreferredCoordiPayload,
    PreferredTagPayload,
    SignupResponse,
    SignupResponseData,
    UserPayload,
)
from app.services.auth_service import authenticate_user, get_user_from_token, register_user

# 인증 관련 라우터(접두사: /auth)
router = APIRouter(prefix="/auth", tags=["Authentication"]) # tags: 문서화 시 그룹화 용도

# 사용자 페이로드(응답 데이터) 생성 헬퍼 함수
def _build_user_payload(user) -> UserPayload:
    """사용자 페이로드 생성 헬퍼 함수"""

    # 프로필 이미지 URL 추출
    profile_image_url = (
        user.images[0].image_url if getattr(user, "images", []) else None
    )

    # 선호 태그 추출
    preferred_tags = None
    if user.preferred_tags:
        preferred_tags = [
            PreferredTagPayload(id=tag.tag.tag_id, name=tag.tag.name)
            for tag in user.preferred_tags
        ]

    # 선호 코디 추출
    preferred_coordis = None
    preference_interactions = [
        interaction for interaction in user.coordi_interactions 
        if interaction.action_type == 'preference'
    ]
    if preference_interactions:
        preferred_coordis = []
        for interaction in preference_interactions:
            coordi = interaction.coordi
            # 메인 이미지 찾기 (is_main=True 우선, 없으면 첫 번째 이미지)
            main_image = next(
                (img for img in coordi.images if img.is_main),
                coordi.images[0] if coordi.images else None
            )
            main_image_url = main_image.image_url if main_image else None
            
            preferred_coordis.append(
                PreferredCoordiPayload(
                    id=coordi.coordi_id,
                    style=coordi.style,
                    season=coordi.season,
                    gender=coordi.gender,
                    description=coordi.description,
                    mainImageUrl=main_image_url,
                    preferredAt=interaction.interacted_at
                )
            )

    # 사용자 페이로드 생성
    return UserPayload.model_validate(
        {
            "id": user.user_id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "profileImageUrl": profile_image_url,
            "preferredTags": preferred_tags,
            "preferredCoordis": preferred_coordis,
            "hasCompletedOnboarding": user.has_completed_onboarding,
            "createdAt": user.created_at,
        },
        from_attributes=False,
    )

# 신규 사용자 회원가입 API
@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
)
def signup(
    payload: UserCreateRequest, # 사용자 생성 요청 페이로드
    db: Session = Depends(get_db), # 데이터베이스 세션
) -> SignupResponse:
    """신규 사용자 회원가입 엔드포인트."""

    # 사용자 등록
    user = register_user(db, payload)

    # 사용자 페이로드 생성
    user_payload = _build_user_payload(user)

    # 사용자 응답 반환
    return SignupResponse(
        data=SignupResponseData(
            user=user_payload,
        )
    )


# 기존 사용자 로그인 API
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
def login(
    payload: UserLoginRequest, 
    db: Session = Depends(get_db)
) -> LoginResponse:
    """기존 사용자 로그인 엔드포인트."""

    # 사용자 인증
    user, token = authenticate_user(db, payload)

    # 사용자 페이로드 생성
    user_payload = _build_user_payload(user)

    # 로그인 응답 반환
    return LoginResponse(
        data=LoginResponseData(
            user=user_payload,
            token=token,
        )
    )

# 기존 사용자 로그아웃 API
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
def logout(authorization: str = Header(...)) -> LogoutResponse:
    """로그아웃 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 토큰 검증
    decode_access_token(token)

    # 로그아웃 응답 반환
    return LogoutResponse(
        success=True,
        message="로그아웃되었습니다",
    )

# 현재 로그인한 사용자 정보 조회 API
@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=MeResponse,
)
def read_current_user(
    authorization: str = Header(...), # 인증 헤더
    db: Session = Depends(get_db),
) -> MeResponse:
    """현재 로그인한 사용자 정보 조회 엔드포인트."""

    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)

    # 서비스 계층에서 사용자 조회
    user = get_user_from_token(db, token)

    # 사용자 페이로드 생성
    user_payload = _build_user_payload(user)

    # 내 정보 조회 응답 반환
    return MeResponse(
        data=MeResponseData(
            user=user_payload,
        )
    )


