"""
스토리지 서비스 추상화 및 구현 (Local / GCS).
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import io
import aiofiles
import boto3
from botocore.exceptions import ClientError

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


class S3StorageService(StorageService):
    """AWS S3 스토리지 서비스"""

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        bucket_name: str
    ):
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        # Boto3 Client 생성
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    async def upload(self, content: bytes, destination: str, mime_type: str = "application/octet-stream") -> str:
        import asyncio
        
        def _upload_sync():
            file_obj = io.BytesIO(content)
            try:
                # S3 업로드 (Content-Type 설정)
                self.s3_client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    destination, # destination is the filename/key
                    ExtraArgs={'ContentType': mime_type} # ACL='public-read' 제거 (버킷 정책 권장)
                )
                
                # 퍼블릭 URL 생성 (가상 호스팅 방식)
                # https://{bucket_name}.s3.{region_name}.amazonaws.com/{filename}
                url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{destination}"
                
                logger.info(f"S3 upload success: {url}")
                return url
                
            except ClientError as e:
                logger.error(f"S3 upload failed: {e}")
                raise

        try:
            url = await asyncio.to_thread(_upload_sync)
            return url
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise e

    async def delete(self, file_path: str) -> bool:
        import asyncio
        
        def _delete_sync():
            try:
                # URL에서 파일 키(Key) 추출
                # 예: https://bucket.s3.region.amazonaws.com/folder/image.jpg -> folder/image.jpg
                if "amazonaws.com/" in file_path:
                    key = file_path.split("amazonaws.com/")[-1]
                else:
                    # URL 형식이 다르거나 이미 키만 넘어온 경우
                    key = file_path
                    
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"S3 delete success: {key}")
                return True
                
            except ClientError as e:
                logger.error(f"S3 delete failed: {e}")
                return False

        try:
            result = await asyncio.to_thread(_delete_sync)
            return result
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False



def get_storage_service() -> StorageService:
    """환경 변수에 따라 적절한 StorageService 인스턴스를 반환합니다."""
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "s3":
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_REGION", "ap-northeast-2")
        bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        
        if not (access_key and secret_key and bucket_name):
            logger.warning("AWS S3 credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME) not fully set, falling back to local storage")
            return LocalStorageService()
            
        return S3StorageService(access_key, secret_key, region, bucket_name)
    
    return LocalStorageService()

