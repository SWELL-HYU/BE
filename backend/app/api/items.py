"""
아이템 관련 API 라우터.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.security import extract_bearer_token
from app.db.database import get_db
from app.schemas.items import ItemDetailPayload, ItemDetailResponse, ItemDetailResponseData
from app.services.auth_service import get_user_from_token
from app.services.item_service import get_item_by_id

# 아이템 관련 라우터(접두사: /items)
router = APIRouter(prefix="/items", tags=["Items"]) # tags: 문서화 시 그룹화 용도

# 아이템 페이로드(응답 데이터) 헬퍼 함수
def _build_item_payload(item) -> ItemDetailPayload:

    # 메인 이미지 추출
    # 메인 이미지가 있으면 메인 이미지 URL을 사용, 없으면 첫 번째 이미지 URL을 사용
    main_image: Optional[str] = None
    if getattr(item, "images", None):
        main_image = next(
            (image.image_url for image in item.images if getattr(image, "is_main", False)),
            item.images[0].image_url,
        )

    # 아이템 페이로드 생성
    payload = ItemDetailPayload.model_validate(
        {
            "id": str(item.item_id),
            "category": item.item_type,
            "brand": item.brand_name_ko,
            "name": item.item_name,
            "price": float(item.price) if item.price is not None else None,
            "imageUrl": main_image,
            "purchaseUrl": item.purchase_url,
            "createdAt": item.created_at,
        },
        from_attributes=False,
    )

    return payload

# 아이템 상세 정보 조회 API
@router.get(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ItemDetailResponse,
)
def read_item_detail(
    item_id: int, # 아이템 ID
    authorization: str = Header(...), # 인증 헤더
    db: Session = Depends(get_db), # 데이터베이스 세션
) -> ItemDetailResponse:
    """
    아이템 상세 정보를 조회한다.
    """

    # 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 사용자 조회
    get_user_from_token(db, token)

    # 아이템 조회
    item = get_item_by_id(db, item_id)

    # 아이템 페이로드 생성
    item_payload = _build_item_payload(item)

    # 아이템 상세 정보 응답 반환
    return ItemDetailResponse(
        data=ItemDetailResponseData(
            item=item_payload,
        )
    )


