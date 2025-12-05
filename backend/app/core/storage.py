"""
스토리지 서비스 추상화 및 구현 (Local / GCS).
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import aiofiles
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """스토리지 서비스 추상 클래스"""

    @abstractmethod
    async def upload(self, content: bytes, destination: str, mime_type: str = "application/octet-stream") -> str:
        """
        파일을 업로드합니다.

        Args:
            content: 파일 내용 (bytes)
            destination: 저장 경로 (파일명 포함, 예: "users/1/profile.jpg")
            mime_type: MIME 타입

        Returns:
            업로드된 파일의 접근 가능한 URL (또는 경로)
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        파일을 삭제합니다.

        Args:
            file_path: 파일 경로 (upload 메서드가 반환한 값)

        Returns:
            삭제 성공 여부
        """
        pass


class LocalStorageService(StorageService):
    """로컬 파일 시스템 스토리지 서비스"""

    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, content: bytes, destination: str, mime_type: str = "application/octet-stream") -> str:
        # 절대 경로 생성
        full_path = self.base_dir / destination
        
        # 상위 디렉토리 생성
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 쓰기 (비동기)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
            
        logger.info(f"Local storage upload success: {full_path}")
        
        # URL 경로 반환 (예: /uploads/users/1/profile.jpg)
        # 주의: destination이 "users/1/profile.jpg"라면 반환값은 "/uploads/users/1/profile.jpg"
        return f"/{self.base_dir.as_posix()}/{destination}"

    async def delete(self, file_path: str) -> bool:
        try:
            # URL 경로에서 실제 파일 경로로 변환
            # 예: "/uploads/users/1/profile.jpg" -> "uploads/users/1/profile.jpg"
            if file_path.startswith("/"):
                file_path = file_path.lstrip("/")
            
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Local storage delete success: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Local storage delete failed: {e}")
            return False


class GCSStorageService(StorageService):
    """Google Cloud Storage 서비스"""

    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            # 환경 변수(GOOGLE_APPLICATION_CREDENTIALS) 또는 기본 인증 사용
            self.client = storage.Client()
            
        self.bucket = self.client.bucket(bucket_name)

    async def upload(self, content: bytes, destination: str, mime_type: str = "application/octet-stream") -> str:
        # GCS는 동기 라이브러리이므로, 블로킹 방지를 위해 별도 스레드 등 고려 가능하지만
        # 여기서는 간단히 구현 (필요 시 asyncio.to_thread 사용)
        import asyncio
        
        def _upload_sync():
            blob = self.bucket.blob(destination)
            blob.upload_from_string(content, content_type=mime_type)
            # 공개 URL 반환 (버킷이 공개 설정되어 있다고 가정)
            # 또는 blob.public_url 사용
            return f"https://storage.googleapis.com/{self.bucket_name}/{destination}"

        try:
            url = await asyncio.to_thread(_upload_sync)
            logger.info(f"GCS upload success: {url}")
            return url
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            raise e

    async def delete(self, file_path: str) -> bool:
        import asyncio
        
        def _delete_sync():
            # URL에서 객체 이름 추출
            # 예: https://storage.googleapis.com/bucket-name/users/1/profile.jpg -> users/1/profile.jpg
            prefix = f"https://storage.googleapis.com/{self.bucket_name}/"
            if file_path.startswith(prefix):
                blob_name = file_path[len(prefix):]
            else:
                # URL이 아닌 경우 그대로 시도
                blob_name = file_path
                
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                return True
            return False

        try:
            result = await asyncio.to_thread(_delete_sync)
            if result:
                logger.info(f"GCS delete success: {file_path}")
            return result
        except Exception as e:
            logger.error(f"GCS delete failed: {e}")
            return False


def get_storage_service() -> StorageService:
    """환경 변수에 따라 적절한 StorageService 인스턴스를 반환합니다."""
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "gcs":
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        credentials_path = os.getenv("GCS_CREDENTIALS_PATH")
        
        if not bucket_name:
            logger.warning("GCS_BUCKET_NAME not set, falling back to local storage")
            return LocalStorageService()
            
        return GCSStorageService(bucket_name, credentials_path)
    
    return LocalStorageService()
