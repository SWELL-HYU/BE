"""
가상 피팅 관련 비즈니스 로직.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import List, Union

import aiofiles
import httpx
from google.genai import Client, types
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    DuplicateCategoryError,
    ForbiddenError,
    FittingJobNotFoundError,
    InsufficientItemsError,
    InvalidCategoryError,
    InvalidItemIdError,
    ItemNotFoundError,
    PhotoRequiredError,
    TooManyItemsError,
)
from app.core.file_utils import ensure_upload_directory
from app.models.fitting_result import FittingResult
from app.models.fitting_result_image import FittingResultImage
from app.models.fitting_result_item import FittingResultItem
from app.models.item import Item
from app.models.user_image import UserImage
from app.schemas.user_request import FittingItemRequest, VirtualFittingRequest
from app.schemas.recommendation_response import PaginationPayload
from app.schemas.user_response import (
    FittingHistoryItemPayload,
    FittingHistoryPayload,
    FittingHistoryResponseData,
    VirtualFittingJobStatusCompletedPayload,
    VirtualFittingJobStatusFailedPayload,
    VirtualFittingJobStatusPayload,
    VirtualFittingJobStatusProcessingPayload,
    VirtualFittingJobStatusTimeoutPayload,
)

logger = logging.getLogger(__name__)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL_ID")
FITTING_TIMEOUT_SECONDS = 300.0  # 5분 타임아웃


def start_virtual_fitting(
    db: Session,
    user_id: int,
    request: VirtualFittingRequest,
) -> int:
    """
    가상 피팅 작업을 시작합니다.
    
    Parameters
    ----------
    db:
        데이터베이스 세션
    user_id:
        사용자 ID
    request:
        가상 피팅 요청 데이터
        
    Returns
    -------
    int:
        피팅 작업 ID (fitting_id)
        
    Raises
    ------
    PhotoRequiredError:
        사용자 사진이 업로드되지 않은 경우
    InsufficientItemsError:
        아이템이 1개 미만인 경우
    TooManyItemsError:
        아이템이 3개 초과인 경우
    DuplicateCategoryError:
        동일한 카테고리의 아이템이 중복된 경우
    InvalidCategoryError:
        유효하지 않은 카테고리인 경우
    InvalidItemIdError:
        유효하지 않은 아이템 ID가 포함된 경우
    """
    # 1. 사용자 사진 존재 확인 (UserImage 테이블에서 조회)
    user_image = db.execute(
        select(UserImage)
        .where(UserImage.user_id == user_id)
        .order_by(UserImage.created_at.desc())
    ).scalar_one_or_none()
    
    if user_image is None:
        raise PhotoRequiredError()
    
    # 2. 아이템 개수 검증
    items = request.items
    if len(items) < 1:
        raise InsufficientItemsError()
    if len(items) > 3:
        raise TooManyItemsError(message="최대 3개의 아이템만 선택할 수 있습니다")
    
    # 3. 카테고리 중복 확인 및 유효성 검증
    categories_seen = set()
    item_ids = []
    
    for item in items:
        # 카테고리 유효성 확인
        if item.category not in ("top", "bottom", "outer"):
            raise InvalidCategoryError()
        
        # 카테고리 중복 확인
        if item.category in categories_seen:
            raise DuplicateCategoryError()
        categories_seen.add(item.category)
        
        item_ids.append(item.item_id)
    
    # 4. 아이템 ID 유효성 확인
    existing_items = db.execute(
        select(Item).where(Item.item_id.in_(item_ids))
    ).scalars().all()
    
    if len(existing_items) != len(item_ids):
        raise InvalidItemIdError()
    
    # 5. FittingResult 레코드 생성
    fitting_result = FittingResult(
        user_id=user_id,
        status="processing",
    )
    db.add(fitting_result)
    db.flush()  # fitting_id를 얻기 위해 flush
    
    # 6. FittingResultItem 레코드 생성
    for item in items:
        fitting_result_item = FittingResultItem(
            fitting_id=fitting_result.fitting_id,
            item_id=item.item_id,
        )
        db.add(fitting_result_item)
    
    db.commit()
    db.refresh(fitting_result)
    
    return fitting_result.fitting_id


async def _download_image(url: str, timeout: float = 10.0) -> tuple[bytes, str] | None:
    """
    URL 또는 파일 경로에서 이미지를 다운로드합니다.
    
    Parameters
    ----------
    url:
        이미지 URL 또는 파일 경로
    timeout:
        타임아웃 (초, HTTP 요청에만 적용)
        
    Returns
    -------
    tuple[bytes, str] | None:
        (이미지 bytes, MIME 타입) 또는 None (실패 시)
    """
    try:
        # 상대 경로인 경우 파일 시스템에서 읽기
        # TODO: 배포시 저장 경로 수정
        if url.startswith("/") and not url.startswith(("http://", "https://")):
            # 상대 경로를 절대 경로로 변환 (uploads 디렉토리 기준)
            file_path = Path(url.lstrip("/"))
            if not file_path.is_absolute():
                # 상대 경로인 경우 현재 작업 디렉토리 기준
                file_path = Path.cwd() / file_path
            
            if not file_path.exists():
                logger.error(f"파일을 찾을 수 없습니다: {file_path}")
                return None
            
            # 파일 읽기
            image_bytes = await asyncio.to_thread(file_path.read_bytes)
            
            # MIME 타입 추정 (파일 확장자 기반)
            mime_type = "image/jpeg"  # 기본값
            url_lower = url.lower()
            if url_lower.endswith((".png",)):
                mime_type = "image/png"
            elif url_lower.endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            
            return image_bytes, mime_type
        
        # HTTP/HTTPS URL인 경우 기존 방식 사용
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            image_bytes = response.content
            
            # MIME 타입 추정 (URL 확장자 기반)
            mime_type = "image/jpeg"  # 기본값
            url_lower = url.lower()
            if url_lower.endswith((".png",)):
                mime_type = "image/png"
            elif url_lower.endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            
            return image_bytes, mime_type
    except Exception as e:
        logger.error(f"이미지 다운로드 실패: {url}, 에러: {e}")
        return None


def _generate_fitting_image_single_step_sync(
    person_or_result_image_bytes: bytes,
    person_or_result_mime_type: str,
    garment_image_bytes: bytes,
    garment_mime_type: str,
    canvas_image_bytes: bytes,
    canvas_mime_type: str,
) -> bytes | None:
    """
    동기 방식으로 Gemini API를 호출하여 단일 단계 가상 피팅 이미지를 생성합니다.
    
    Parameters
    ----------
    person_or_result_image_bytes:
        사람 이미지 또는 이전 단계 결과 이미지 bytes
    person_or_result_mime_type:
        사람 이미지 또는 결과 이미지 MIME 타입
    garment_image_bytes:
        의류 이미지 bytes (단일)
    garment_mime_type:
        의류 이미지 MIME 타입
    canvas_image_bytes:
        캔버스 이미지 bytes
    canvas_mime_type:
        캔버스 이미지 MIME 타입
        
    Returns
    -------
    bytes | None:
        생성된 이미지 bytes 또는 None (실패 시)
    """
    try:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY가 설정되지 않았습니다")
            return None
        
        client = Client(api_key=GEMINI_API_KEY)
        
        # TODO: 프롬프트 구성 (단일 garment용)
        # TODO: 진짜 무조건 바꿔야됨. 분기처리하던지 좀 싀발
        enhanced_prompt = (
            "Role: You are a professional virtual try-on artist specialized in realistic garment dressing.\n"
            "Input structure:\n"
            " - Image[1]: Person image (the model to be dressed, centered in frame)\n"
            " - Image[2]: Garment image (to be worn on the person)\n"
            " - Image[3]: Final background canvas\n\n"
            "Objective: Dress the centered person in Image[1] with the garment from Image[2], "
            "as if physically worn on the body. "
            "After the person is dressed, place and paint the result directly onto the final background canvas (Image[3]).\n\n"
            "Canvas priority: The final composition must fit perfectly onto the provided canvas dimensions. "
            "Do not resize, crop, pad, rotate, or move the person or the canvas.\n\n"
            "Garment dressing process: Simulate realistic clothing wear — position it accurately over the body, "
            "fit the sleeves, collar, and hem naturally, follow body curvature, and reproduce realistic tension, stretch, and fabric folds. "
            "Warp and deform only the garment (never the person) to achieve a perfect anatomical fit. "
            "Blend lighting, color, and shadows so the clothing appears genuinely worn rather than overlaid.\n\n"
            "Preserve: Maintain the person's pose, proportions, facial features, hair, skin tone, accessories, and background environment. "
            "Only modify areas necessary to make the garment appear truly worn.\n\n"
            "Restrictions: Do not invent new objects, duplicate or erase body parts, distort anatomy, or alter the person's position.\n\n"
            "Output: A single high-quality PNG image of the person realistically wearing the provided garment, "
            "painted seamlessly onto the supplied background canvas."
        )
        
        # 이미지 파트 생성
        person_or_result_part = types.Part.from_bytes(
            data=person_or_result_image_bytes,
            mime_type=person_or_result_mime_type
        )
        garment_part = types.Part.from_bytes(
            data=garment_image_bytes,
            mime_type=garment_mime_type
        )
        canvas_part = types.Part.from_bytes(
            data=canvas_image_bytes,
            mime_type=canvas_mime_type
        )
        
        # 콘텐츠 구성
        contents = [enhanced_prompt, person_or_result_part, garment_part, canvas_part]
        
        # Gemini API 호출
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )
        
        # 응답에서 이미지 추출
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        
        logger.error("응답에서 편집된 이미지를 찾지 못했습니다")
        return None
        
    except Exception as e:
        logger.error(f"Gemini API 호출 실패: {e}")
        return None


def _generate_llm_message_sync(
    image_bytes: bytes,
    mime_type: str,
) -> str | None:
    """
    동기 방식으로 Gemini API를 호출하여 가상 피팅 결과 이미지에 대한 추천 메시지를 생성합니다.
    
    Parameters
    ----------
    image_bytes:
        가상 피팅 결과 이미지 bytes
    mime_type:
        이미지 MIME 타입
        
    Returns
    -------
    str | None:
        생성된 LLM 메시지. 실패 시 None 반환.
    """
    try:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY가 설정되지 않았습니다")
            return None
        
        client = Client(api_key=GEMINI_API_KEY)
        
        # 프롬프트 구성
        # TODO: 프롬프트 수정
        prompt = (
            "이 가상 피팅 결과 이미지를 보고 사용자에게 친근하고 매력적인 추천 메시지를 작성해주세요. "
            "한 문장으로, 이모지를 포함하여 작성해주세요. (최대 50자)"
        )
        
        # 이미지 파트 생성
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )
        
        # 콘텐츠 구성
        contents = [prompt, image_part]
        
        # Gemini API 호출
        response = client.models.generate_content(
            model="gemini-2.5-flash", # TODO: 모델 변경 가능
            contents=contents,
        )
        
        # 응답 텍스트 추출
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        
        return None
    except Exception as e:
        logger.error(f"LLM 메시지 생성 실패: {e}")
        return None


async def _process_virtual_fitting_async(
    db: Session,
    fitting_id: int,
    user_id: int,
    items: List[FittingItemRequest],
) -> None:
    """
    가상 피팅 처리를 비동기로 수행합니다.
    
    Parameters
    ----------
    db:
        데이터베이스 세션
    fitting_id:
        피팅 작업 ID
    user_id:
        사용자 ID
    items:
        피팅할 아이템 목록
    """
    try:
        # 1. 이미지 다운로드
        logger.info(f"가상 피팅 처리 시작: fitting_id={fitting_id}")
        
        # 사용자 사진 조회 (UserImage 테이블에서)
        user_image = db.execute(
            select(UserImage)
            .where(UserImage.user_id == user_id)
            .order_by(UserImage.created_at.desc())
        ).scalar_one_or_none()
        
        if user_image is None:
            raise PhotoRequiredError()
        
        # 사람 이미지 다운로드
        person_result = await _download_image(user_image.image_url)
        if person_result is None:
            raise Exception("사용자 사진 다운로드 실패")
        person_image_bytes, person_mime_type = person_result
        
        # 의류 이미지 다운로드
        garment_results = []
        for item in items:
            result = await _download_image(item.image_url)
            if result is None:
                raise Exception(f"아이템 이미지 다운로드 실패: item_id={item.item_id}")
            garment_results.append(result)
        
        # 캔버스 생성 (사람 이미지 크기 기준)
        person_image = Image.open(BytesIO(person_image_bytes))
        original_width, original_height = person_image.size
        
        canvas_mode = "RGBA" if person_image.mode == "RGBA" else "RGB"
        canvas_fill = (255, 255, 255, 0) if canvas_mode == "RGBA" else (255, 255, 255)
        canvas_image = Image.new(canvas_mode, (original_width, original_height), canvas_fill)
        
        # 캔버스를 bytes로 변환
        with BytesIO() as buffer:
            canvas_image.save(buffer, format="PNG")
            canvas_image_bytes = buffer.getvalue()
        canvas_mime_type = "image/png"
        
        # 2. FittingResult 조회
        fitting_result = db.get(FittingResult, fitting_id)
        if fitting_result is None:
            logger.error(f"FittingResult를 찾을 수 없습니다: fitting_id={fitting_id}")
            return
        
        # 3. 순차적 피팅 처리
        current_image_bytes = person_image_bytes
        current_mime_type = person_mime_type
        
        # 전체 작업에 대한 타임아웃 적용
        async def sequential_fitting():
            nonlocal current_image_bytes, current_mime_type
            
            for i, (item, garment_result) in enumerate(zip(items, garment_results)):
                garment_bytes, garment_mime = garment_result
                
                # current_step 업데이트
                fitting_result.current_step = item.category
                db.commit()
                logger.info(f"피팅 단계 진행: fitting_id={fitting_id}, step={item.category}")
                
                # 단일 단계 피팅 호출
                result_image = await asyncio.to_thread(
                    _generate_fitting_image_single_step_sync,
                    current_image_bytes,
                    current_mime_type,
                    garment_bytes,
                    garment_mime,
                    canvas_image_bytes,
                    canvas_mime_type,
                )
                
                if result_image is None:
                    # 실패 처리
                    fitting_result.failed_step = item.category
                    db.commit()
                    raise Exception(f"피팅 실패: {item.category}")
                
                # 다음 단계를 위해 현재 이미지 업데이트
                current_image_bytes = result_image
                current_mime_type = "image/png"  # Gemini 응답은 PNG
            
            return current_image_bytes
        
        # 순차적 피팅 실행 (전체 타임아웃 적용)
        final_image_bytes = await asyncio.wait_for(
            sequential_fitting(),
            timeout=FITTING_TIMEOUT_SECONDS,
        )
        
        # 4. LLM 메시지 생성 (최종 이미지로)
        logger.info(f"LLM 메시지 생성 시작: fitting_id={fitting_id}")
        llm_message = await asyncio.wait_for(
            asyncio.to_thread(
                _generate_llm_message_sync,
                final_image_bytes,
                "image/png",
            ),
            timeout=15.0,  # LLM 타임아웃
        )
        
        # 5. 결과 이미지 저장
        # TODO: 배포시 저장 경로 수정
        upload_dir = Path("uploads") / "fitting"
        ensure_upload_directory(upload_dir)
        
        filename = f"fitting_{fitting_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
        file_path = upload_dir / filename
        
        # 비동기 파일 저장
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(final_image_bytes)
        
        # 상대 경로 생성 (URL용)
        relative_path = f"/{upload_dir.as_posix()}/{filename}"
        
        # 6. FittingResult 상태 업데이트 및 이미지 저장
        fitting_result.status = "completed"
        fitting_result.finished_at = datetime.now(timezone.utc)
        fitting_result.current_step = None  # 완료 시 current_step 초기화
        if llm_message:
            fitting_result.llm_message = llm_message
        
        fitting_result_image = FittingResultImage(
            fitting_id=fitting_id,
            image_url=relative_path,
        )
        db.add(fitting_result_image)
        
        db.commit()
        
        logger.info(f"가상 피팅 처리 완료: fitting_id={fitting_id}")
        
    except asyncio.TimeoutError:
        logger.error(f"가상 피팅 처리 타임아웃: fitting_id={fitting_id}")
        fitting_result = db.get(FittingResult, fitting_id)
        if fitting_result:
            fitting_result.status = "timeout"
            fitting_result.finished_at = datetime.now(timezone.utc)
            fitting_result.current_step = None
            db.commit()
    except Exception as e:
        logger.error(f"가상 피팅 처리 실패: fitting_id={fitting_id}, 에러: {e}")
        fitting_result = db.get(FittingResult, fitting_id)
        if fitting_result:
            fitting_result.status = "failed"
            fitting_result.finished_at = datetime.now(timezone.utc)
            # failed_step은 이미 sequential_fitting()에서 설정됨
            fitting_result.current_step = None
            db.commit()


# 카테고리명 한글 매핑
CATEGORY_NAME_MAP = {
    "top": "상의",
    "bottom": "하의",
    "outer": "아우터",
}


def get_virtual_fitting_status(
    db: Session,
    fitting_id: int,
    user_id: int,
) -> VirtualFittingJobStatusPayload:
    """
    가상 피팅 작업의 상태를 조회합니다.
    
    Parameters
    ----------
    db:
        데이터베이스 세션
    fitting_id:
        피팅 작업 ID
    user_id:
        사용자 ID
        
    Returns
    -------
    VirtualFittingJobStatusPayload:
        상태별 페이로드 (Processing, Completed, Failed, Timeout)
        
    Raises
    ------
    FittingJobNotFoundError:
        피팅 작업을 찾을 수 없는 경우
    ForbiddenError:
        다른 사용자의 작업에 접근하려는 경우
    """
    # 1. FittingResult 조회
    fitting_result = db.get(FittingResult, fitting_id)
    if fitting_result is None:
        raise FittingJobNotFoundError()
    
    # 2. 권한 확인
    if fitting_result.user_id != user_id:
        raise ForbiddenError()
    
    # 3. 상태별 페이로드 생성
    status = fitting_result.status
    
    if status == "processing":
        # Processing 상태
        if fitting_result.current_step is None:
            # current_step이 None인 경우는 없어야 하지만, 안전을 위해 처리
            current_step = "top"
        else:
            current_step = fitting_result.current_step
        
        return VirtualFittingJobStatusProcessingPayload(
            jobId=fitting_id,
            status="processing",
            currentStep=current_step,
        )
    
    elif status == "completed":
        # Completed 상태
        # 이미지 URL 조회 (하나의 이미지만 존재)
        if not fitting_result.images:
            # 이미지가 없는 경우는 없어야 하지만, 안전을 위해 처리
            raise FittingJobNotFoundError()
        
        result_image_url = fitting_result.images[0].image_url
        
        # LLM 메시지 처리
        llm_message = fitting_result.llm_message
        if llm_message is None:
            llm_message = "메시지 생성 중 오류가 발생했습니다"
        
        # processingTime 계산
        if fitting_result.finished_at and fitting_result.created_at:
            processing_time = int(
                (fitting_result.finished_at - fitting_result.created_at).total_seconds()
            )
        else:
            processing_time = 0
        
        return VirtualFittingJobStatusCompletedPayload(
            jobId=fitting_id,
            status="completed",
            resultImageUrl=result_image_url,
            llmMessage=llm_message,
            completedAt=fitting_result.finished_at,
            processingTime=processing_time,
        )
    
    elif status == "failed":
        # Failed 상태
        # 에러 메시지 동적 생성
        if fitting_result.failed_step:
            category_name = CATEGORY_NAME_MAP.get(
                fitting_result.failed_step,
                fitting_result.failed_step,
            )
            error_message = f"{category_name} 피팅 중 오류가 발생했습니다"
        else:
            error_message = "피팅 중 오류가 발생했습니다"
        
        return VirtualFittingJobStatusFailedPayload(
            jobId=fitting_id,
            status="failed",
            error=error_message,
            failedStep=fitting_result.failed_step or "unknown",
            failedAt=fitting_result.finished_at,
        )
    
    elif status == "timeout":
        # Timeout 상태
        # 에러 메시지 동적 생성
        error_message = f"처리 시간을 초과했습니다 ({int(FITTING_TIMEOUT_SECONDS)}초)"
        
        return VirtualFittingJobStatusTimeoutPayload(
            jobId=fitting_id,
            status="timeout",
            error=error_message,
            timeoutAt=fitting_result.finished_at,
        )
    
    else:
        # 알 수 없는 상태
        raise FittingJobNotFoundError()


def get_virtual_fitting_history(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = 20,
) -> FittingHistoryResponseData:
    """
    가상 피팅 이력을 조회합니다.
    
    Parameters
    ----------
    db:
        데이터베이스 세션
    user_id:
        사용자 ID
    page:
        페이지 번호 (기본값: 1)
    limit:
        페이지당 개수 (기본값: 20)
        
    Returns
    -------
    FittingHistoryResponseData:
        가상 피팅 이력 및 페이지네이션 정보
    """
    # 1. 전체 개수 조회
    count_query = select(func.count(FittingResult.fitting_id)).where(
        FittingResult.user_id == user_id
    )
    total_items = db.execute(count_query).scalar_one()
    
    # 결과가 없으면 빈 결과 반환
    if total_items == 0:
        return FittingHistoryResponseData(
            fittings=[],
            pagination=PaginationPayload(
                currentPage=page,
                totalPages=0,
                totalItems=0,
                hasNext=False,
                hasPrev=False,
            ),
        )
    
    # 2. 페이지네이션 적용 및 정렬 (created_at 기준 최신순)
    offset = (page - 1) * limit
    fitting_results = db.execute(
        select(FittingResult)
        .where(FittingResult.user_id == user_id)
        .order_by(FittingResult.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(FittingResult.fitting_result_items).selectinload(
                FittingResultItem.item
            ),
            selectinload(FittingResult.images),
        )
    ).scalars().all()
    
    # 3. 페이로드 생성
    fittings = []
    for fitting_result in fitting_results:
        # resultImageUrl 처리
        result_image_url = None
        if fitting_result.status == "completed" and fitting_result.images:
            result_image_url = fitting_result.images[0].image_url
        
        # 아이템 정보 수집
        items = [
            FittingHistoryItemPayload(
                itemId=fitting_item.item.item_id,
                category=fitting_item.item.category,
                name=fitting_item.item.item_name,
            )
            for fitting_item in fitting_result.fitting_result_items
        ]
        
        fittings.append(
            FittingHistoryPayload(
                jobId=fitting_result.fitting_id,
                status=fitting_result.status,
                resultImageUrl=result_image_url,
                items=items,
                createdAt=fitting_result.created_at,
            )
        )
    
    # 4. 페이지네이션 정보 계산
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    return FittingHistoryResponseData(
        fittings=fittings,
        pagination=PaginationPayload(
            currentPage=page,
            totalPages=total_pages,
            totalItems=total_items,
            hasNext=has_next,
            hasPrev=has_prev,
        ),
    )


def delete_virtual_fitting_history(
    db: Session,
    fitting_id: int,
    user_id: int,
) -> datetime:
    """
    가상 피팅 이력을 삭제합니다.
    
    Parameters
    ----------
    db:
        데이터베이스 세션
    fitting_id:
        피팅 작업 ID
    user_id:
        사용자 ID
        
    Returns
    -------
    datetime:
        삭제 일시 (UTC)
        
    Raises
    ------
    FittingJobNotFoundError:
        피팅 작업을 찾을 수 없는 경우
    ForbiddenError:
        다른 사용자의 작업을 삭제하려는 경우
    """
    # 1. FittingResult 조회
    fitting_result = db.get(FittingResult, fitting_id)
    if fitting_result is None:
        raise FittingJobNotFoundError()
    
    # 2. 권한 확인
    if fitting_result.user_id != user_id:
        raise ForbiddenError()
    
    # 3. 파일 삭제 (FittingResultImage의 image_url에서)
    try:
        for image in fitting_result.images:
            # 파일 경로 추출 및 삭제
            try:
                file_path = Path(image.image_url.lstrip("/"))
                if not file_path.is_absolute():
                    # 상대 경로인 경우 현재 작업 디렉토리 기준
                    file_path = Path.cwd() / file_path
                
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"가상 피팅 결과 이미지 파일 삭제: {file_path}")
            except Exception as e:
                # 파일 삭제 실패는 로깅하지만 DB 삭제는 계속 진행
                # (파일이 이미 없거나 경로가 잘못된 경우 등)
                logger.warning(
                    f"Failed to delete fitting result image file: {image.image_url}. Error: {e}",
                    exc_info=True,
                )
    except Exception as e:
        # 파일 삭제 중 예외 발생 시에도 로깅만 하고 계속 진행
        logger.warning(
            f"Error while deleting fitting result image files: {e}",
            exc_info=True,
        )
    
    # 4. FittingResult 삭제 (CASCADE로 관련 데이터 자동 삭제)
    db.delete(fitting_result)
    db.commit()
    
    # 5. 삭제 일시 반환
    return datetime.now(timezone.utc)

