"""
인증 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_request import UserCreateRequest, UserLoginRequest
from app.schemas.user_response import (
    LoginResponse,
    LoginResponseData,
    LogoutResponse,
    MeResponse,
    MeResponseData,
    SignupResponse,
    SignupResponseData,
    UserPayload,
)
from app.services.auth_service import authenticate_user, get_user_from_token, register_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _build_user_payload(user) -> UserPayload:
    """사용자 페이로드 생성 헬퍼 함수"""
    profile_image_url = (
        user.images[0].image_url if getattr(user, "images", []) else None
    )

    return UserPayload.model_validate(
        {
            "id": user.user_id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "profileImageUrl": profile_image_url,
            "createdAt": user.created_at,
        },
        from_attributes=False,
    )

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
)
def signup(payload: UserCreateRequest, db: Session = Depends(get_db)) -> SignupResponse:
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


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
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


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
def logout(authorization: str = Header(...)) -> LogoutResponse:
    """로그아웃 엔드포인트."""

    # 헤더에서 토큰 추출
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError(message="유효한 Authorization 헤더가 필요합니다.")

    # 토큰 검증
    decode_access_token(token)

    # 로그아웃 응답 반환
    return LogoutResponse(
        success=True,
        message="로그아웃되었습니다",
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=MeResponse,
)
def read_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> MeResponse:
    """현재 로그인한 사용자 정보 조회 엔드포인트."""

    # 헤더에서 토큰 추출
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError(message="유효한 Authorization 헤더가 필요합니다.")

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


