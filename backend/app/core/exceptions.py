"""
애플리케이션 전역에서 사용하는 커스텀 예외와 FastAPI 핸들러 정의.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """비즈니스 로직에서 사용하는 베이스 예외."""

    code: str = "APP_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "알 수 없는 오류가 발생했습니다."

    def __init__(self, *, message: Optional[str] = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class DuplicateEmailError(AppException):
    """이미 등록된 이메일을 사용할 때 발생하는 예외."""

    code = "EMAIL_EXISTS"
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(message="이미 가입된 이메일입니다.")


class ValidationError(AppException):
    """요청 유효성 검증 실패 시 사용하는 예외."""

    code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *, message: Optional[str] = None) -> None:
        super().__init__(message=message or "입력값을 다시 확인해주세요.")


def register_exception_handlers(app: FastAPI) -> None:
    """커스텀 예외를 FastAPI 인스턴스에 바인딩."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        message = None
        for error in exc.errors():
            loc = error.get("loc", [])
            error_type = error.get("type")
            if loc and loc[-1] == "password" and error_type == "string_too_short":
                message = "비밀번호는 8자 이상이어야 합니다"
                break

        return await app_exception_handler(
            request,
            ValidationError(message=message),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            },
        )


