"""
파일 업로드 관련 유틸리티 함수.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.exceptions import FileRequiredError, FileTooLargeError, InvalidFileFormatError

# 파일 크기 제한: 10MB
# TODO: 특정 조건이 주어질 경우, 교체
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# 허용된 파일 확장자
# TODO: 특정 조건이 주어질 경우, 교체
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# 허용된 MIME 타입 (브라우저/클라이언트가 보내는 파일의 실제 형식)
# 확장자만으로는 부족함(ex. image.exe 파일을 image.jpg 파일로 변조 가능하므로)
# 따라서, 브라우저/클라이언트가 보내는 파일의 실제 형식도 함께 검증하여 보안 강화
# TODO: 특정 조건이 주어질 경우, 교체
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}


def validate_file_format(file: UploadFile) -> None:
    """
    파일 형식을 검증하는 헬퍼 메서드.
    
    Args:
        file: 업로드된 파일
        
    Raises:
        FileRequiredError: 파일이 제공되지 않은 경우
        InvalidFileFormatError: 허용되지 않은 파일 형식인 경우
    """
    # 파일 제공 여부 검증
    if not file or not file.filename:
        raise FileRequiredError()

    # 파일 확장자 검증 (jpg, jpeg, png)
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileFormatError()

    # MIME 타입 검증 (브라우저가 파일 내용을 분석하여 설정한 실제 파일 형식)
    # 확장자만으로는 부족하므로, MIME 타입도 함께 검증하여 보안 강화
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise InvalidFileFormatError()


def validate_file_size(file: UploadFile) -> None:
    """
    파일 크기를 검증하는 헬퍼 메서드.
    
    참고: FastAPI의 UploadFile은 일반적으로 스트리밍 방식으로 처리되지만,
    일부 경우에는 파일이 이미 메모리에 로드되어 file.size 속성을 가질 수 있습니다.
    
    예시:
    - 작은 파일(예: 1MB 이하)은 자동으로 메모리에 로드될 수 있음
    - 클라이언트가 이미 파일 전체를 전송한 경우
    - file.size 속성이 설정된 경우
    
    Args:
        file: 업로드된 파일
        
    Raises:
        FileTooLargeError: 파일 크기가 제한을 초과한 경우
    """
    # 파일 크기 확인 (file.size 속성이 있는 경우 빠른 검증)
    # 일반적으로는 validate_upload_file()에서 파일을 읽어서 크기를 확인합니다
    if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE:
        raise FileTooLargeError()


async def validate_upload_file(file: UploadFile) -> None:
    """
    업로드 파일을 검증하는 헬퍼 메서드 (형식 및 크기).
    
    Args:
        file: 업로드된 파일
        
    Raises:
        FileRequiredError: 파일이 제공되지 않은 경우
        InvalidFileFormatError: 허용되지 않은 파일 형식인 경우
        FileTooLargeError: 파일 크기가 제한을 초과한 경우
    """
    validate_file_format(file)
    
    # 파일 크기 검증 (스트리밍 방식으로 파일을 읽어서 실제 크기 확인)
    # await file.read()는 파일 전체를 작은 조각씩 읽어와서 메모리에 저장합니다
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise FileTooLargeError()
    
    # 파일 포인터를 처음으로 되돌림
    # 파일을 읽은 후 포인터가 끝에 있으므로, 나중에 파일을 다시 읽을 수 있도록 처음으로 되돌립니다
    await file.seek(0)


def generate_unique_filename(original_filename: str) -> str:
    """
    고유한 파일명을 생성하는 헬퍼 메서드.
    
    Args:
        original_filename: 원본 파일명
        
    Returns:
        고유한 파일명 (예: profile_550e8400-e29b-41d4-a716-446655440000.jpg)
    """
    # TODO: 특정 조건이 주어질 경우, 교체
    file_ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:16]  # 짧은 UUID 사용
    return f"profile_{unique_id}{file_ext}"


def get_upload_directory(user_id: int) -> Path:
    """
    사용자별 업로드 디렉토리 경로를 반환하는 헬퍼 메서드.
    TODO: 배포시 변경 고려
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        업로드 디렉토리 Path 객체
    """
    upload_dir = Path("uploads") / "users" / str(user_id)
    return upload_dir


def ensure_upload_directory(upload_dir: Path) -> None:
    """
    업로드 디렉토리가 존재하는지 확인하고, 없으면 생성하는 헬퍼 메서드.
    TODO: 배포시 변경 고려
    
    Args:
        upload_dir: 업로드 디렉토리 Path 객체
    """
    upload_dir.mkdir(parents=True, exist_ok=True)

