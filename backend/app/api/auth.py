"""
인증 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user_request import UserCreateRequest
from app.schemas.user_response import UserPayload, UserResponse, UserResponseData
from app.services.auth_service import register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
def signup(payload: UserCreateRequest, db: Session = Depends(get_db)) -> UserResponse:
    """신규 사용자 회원가입 엔드포인트."""

    user, token = register_user(db, payload)

    profile_image_url = (
        user.images[0].image_url if getattr(user, "images", []) else None
    )

    user_payload = UserPayload.model_validate(
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

    return UserResponse(
        data=UserResponseData(
            user=user_payload,
            token=token,
        )
    )


