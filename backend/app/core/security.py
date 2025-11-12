"""
보안 관련 유틸리티 함수 모음.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "")


def hash_password(password: str) -> str:
    """
    SHA-256 해싱을 사용해 비밀번호를 안전하게 저장 가능한 문자열로 변환한다.

    간단한 솔트를 위해 환경 변수 `PASSWORD_SALT`를 앞에 붙인다.
    """

    digest = hashlib.sha256()
    digest.update(f"{PASSWORD_SALT}{password}".encode("utf-8"))
    return digest.hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """입력된 비밀번호가 저장된 해시와 일치하는지 검증한다."""

    return hmac.compare_digest(hash_password(password), hashed_password)


def create_access_token(
    *,
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    JWT 액세스 토큰을 생성한다.

    Parameters
    ----------
    subject:
        토큰의 주체(subject). 사용자 ID 등을 기대한다.
    expires_delta:
        토큰 만료 시간을 델타로 전달. 미전달 시 기본 설정 사용.
    claims:
        추가로 포함할 클레임 딕셔너리.
    """

    to_encode: Dict[str, Any] = {}
    if claims:
        to_encode.update(claims)

    to_encode.update({"sub": str(subject)})

    expire_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_at = datetime.now(timezone.utc) + expire_delta
    to_encode["exp"] = expire_at

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


