"""
옷장 관련 API 라우터.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.security import extract_bearer_token
from app.db.database import get_db
from app.schemas.user_request import SaveClosetItemRequest
from app.schemas.user_response import (
    ClosetItemsResponse,
    DeleteClosetItemResponse,
    SaveClosetItemResponse,
)
from app.services.auth_service import get_user_from_token
from app.services.closet_service import delete_closet_item, get_closet_items, save_closet_item

router = APIRouter(prefix="/closet", tags=["Closet"])

# 카테고리 필터 허용값
CategoryFilter = Literal["all", "top", "bottom", "outer"]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ClosetItemsResponse,
)
async def get_closet_items_endpoint(
    category: CategoryFilter = Query(default="all", description="카테고리 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=20, ge=1, le=50, description="페이지당 개수"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> ClosetItemsResponse:
    """
    옷장에 저장된 아이템 목록을 조회합니다.
    
    카테고리별로 필터링할 수 있으며, 저장 일시 기준 최신순으로 정렬됩니다.
    categoryCounts는 필터와 관계없이 전체 카테고리별 개수를 반환합니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 옷장 아이템 목록 조회
    items, pagination, category_counts = await get_closet_items(
        db=db,
        user_id=user.user_id,
        category=category,
        page=page,
        limit=limit,
    )
    
    # 응답 반환
    return ClosetItemsResponse(
        data={
            "items": items,
            "pagination": pagination,
            "categoryCounts": category_counts,
        }
    )


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=SaveClosetItemResponse,
)
async def save_closet_item_endpoint(
    request: SaveClosetItemRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> SaveClosetItemResponse:
    """
    아이템을 옷장에 저장합니다.
    
    동일한 아이템을 중복으로 저장할 수 없습니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 옷장에 아이템 저장
    saved_at = save_closet_item(
        db=db,
        user_id=user.user_id,
        item_id=request.item_id,
    )
    
    # 응답 반환
    return SaveClosetItemResponse(
        data={
            "message": "옷장에 저장되었습니다",
            "savedAt": saved_at,
        }
    )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteClosetItemResponse,
)
async def delete_closet_item_endpoint(
    item_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> DeleteClosetItemResponse:
    """
    옷장에서 아이템을 삭제합니다.
    
    현재 로그인한 사용자의 옷장에 저장된 아이템만 삭제할 수 있습니다.
    삭제된 아이템은 복구할 수 없습니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 옷장에서 아이템 삭제
    deleted_at = delete_closet_item(
        db=db,
        user_id=user.user_id,
        item_id=item_id,
    )
    
    # 응답 반환
    return DeleteClosetItemResponse(
        data={
            "message": "옷장에서 삭제되었습니다",
            "deletedAt": deleted_at,
        }
    )

