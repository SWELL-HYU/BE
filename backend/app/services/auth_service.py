"""
인증 관련 비즈니스 로직.
"""

from __future__ import annotations

from typing import Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateEmailError, ValidationError
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.schemas.user_request import UserCreateRequest


def register_user(db: Session, payload: UserCreateRequest) -> Tuple[User, str]:
    """
    신규 사용자를 등록하고 액세스 토큰을 발급한다.
    """

    # 이메일 중복 체크
    existing_user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()

    if existing_user is not None:
        raise DuplicateEmailError(payload.email)

    # 비밀번호 유효성 검증
    if len(payload.password) < 8:
        raise ValidationError(message="비밀번호는 8자 이상이어야 합니다")

    # 사용자 생성
    user = User(
        email=payload.email, # 이메일
        password_hash=hash_password(payload.password),
        name=payload.name, # 이름
        gender=payload.gender.value if payload.gender else None, # 성별
        preferred_tags=payload.preferred_tags, # 선호 태그
    )

    # 사용자 추가
    db.add(user)

    # 사용자 추가 실패 시 예외 처리
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError(payload.email) # 이메일 중복 예외 처리(거의 동시에 같은 이메일로 회원가입 시도)

    # 사용자 생성 후 새로운 사용자 정보 조회(ID 조회용)
    db.refresh(user)

    # 액세스 토큰 생성
    token = create_access_token(
        subject=user.user_id,
        claims={
            "email": user.email,
        },
    )

    return user, token


