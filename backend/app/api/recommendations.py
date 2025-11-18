"""
코디 추천 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.security import extract_bearer_token
from app.db.database import get_db
from app.schemas.recommendation_response import (
    RecommendationsResponse,
    RecommendationsResponseData,
)
from app.services.auth_service import get_user_from_token
from app.services.recommendations_service import get_recommended_coordis

# 코디 추천 관련 라우터(접두사: /recommendations)
router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# 코디 추천 조회 API
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=RecommendationsResponse,
)
async def get_recommendations(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=10, ge=1, le=50, description="페이지당 개수"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """
    사용자 맞춤 코디 목록을 조회합니다.
    
    사용자 성별에 맞는 코디를 추천 알고리즘 기반으로 반환합니다.
    각 코디에는 LLM이 생성한 개인화된 메시지가 포함됩니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 추천 코디 조회
    outfits, pagination = await get_recommended_coordis(
        db=db,
        user_id=user.user_id,
        page=page,
        limit=limit,
    )
    
    # 응답 반환
    return RecommendationsResponse(
        data=RecommendationsResponseData(
            outfits=outfits,
            pagination=pagination,
        )
    )

