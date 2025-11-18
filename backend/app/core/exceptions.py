"""
애플리케이션 전역에서 사용하는 커스텀 예외와 FastAPI 핸들러 정의.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# 비즈니스 로직에서 공통으로 사용하는 기본 예외 클래스.
# 아래에 정의된 각종 도메인 예외(DuplicateEmailError 등)가 이 클래스를 상속한다.
class AppException(Exception):
    """비즈니스 로직에서 사용하는 베이스 예외."""

    code: str = "APP_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "알 수 없는 오류가 발생했습니다."

    # 예외 메시지 초기화
    def __init__(self, *, message: Optional[str] = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)

# 이미 등록된 이메일을 사용할 때 발생하는 예외
class DuplicateEmailError(AppException):
    """이미 등록된 이메일을 사용할 때 발생하는 예외."""

    code = "EMAIL_EXISTS"
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(message="이미 가입된 이메일입니다.")

# 로그인 시 잘못된 자격 증명을 사용할 때 발생하는 예외
class InvalidCredentialsError(AppException):
    """로그인 시 잘못된 자격 증명을 사용할 때 발생하는 예외."""

    code = "INVALID_CREDENTIALS"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__(message="이메일 또는 비밀번호가 올바르지 않습니다")

# 인증이 필요한 요청에서 토큰이 없거나 유효하지 않을 때 발생하는 예외
class UnauthorizedError(AppException):
    """인증이 필요한 요청에서 토큰이 없거나 유효하지 않을 때 발생하는 예외."""

    code = "UNAUTHORIZED"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, message: Optional[str] = None) -> None:
        super().__init__(message=message or "인증이 필요합니다")

# 요청 유효성 검증 실패 시 발생하는 예외
class ValidationError(AppException):
    """요청 유효성 검증 실패 시 사용하는 예외."""

    code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *, message: Optional[str] = None) -> None:
        super().__init__(message=message or "입력값을 다시 확인해주세요.")

# 요청한 아이템이 존재하지 않을 때 발생하는 예외
class ItemNotFoundError(AppException):
    """요청한 아이템이 존재하지 않을 때 발생하는 예외."""

    code = "ITEM_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self) -> None:
        super().__init__(message="아이템을 찾을 수 없습니다")

# 커스텀 예외 핸들러 등록
def register_exception_handlers(app: FastAPI) -> None:
    """커스텀 예외를 FastAPI 인스턴스에 바인딩."""

    # 요청 유효성 검증 실패 시 발생하는 예외 핸들러
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        message = None
        for error in exc.errors():
            loc = error.get("loc", [])
            error_type = error.get("type")
            field_name = loc[-1] if loc else None
            
            # 이메일 필수값 검증
            if field_name == "email" and error_type == "missing":
                message = "이메일을 입력해주세요"
                break
            # 비밀번호 필수값 검증
            if field_name == "password" and error_type == "missing":
                message = "비밀번호를 입력해주세요"
                break
            # 비밀번호 길이 검증
            if field_name == "password" and error_type == "string_too_short":
                message = "비밀번호가 8자 이상이여야합니다"
                break
            # 성별 필수 검증
            if field_name == "gender" and error_type == "missing":
                message = "성별을 선택해주세요"
                break
            # 이메일 형식 검증
            if field_name == "email" and error_type in ("value_error", "type_error"):
                message = "유효하지 않은 이메일 형식입니다"
                break

        # ValidationError 형식으로 직접 응답 반환
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": message or "요청 유효성 검증에 실패했습니다.",
                },
            },
        )
    
    # 비즈니스 로직에서 발생하는 예외 핸들러(DuplicateEmailError, InvalidCredentialsError, UnauthorizedError, ValidationError, ItemNotFoundError 등)
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


