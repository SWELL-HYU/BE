"""
코디 목록 조회 관련 API 라우터.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.security import extract_bearer_token
from app.db.database import get_db
from app.schemas.recommendation_response import (
    RecommendationsResponse,
    RecommendationsResponseData,
)
from app.schemas.outfits import (
    AddFavoriteResponse,
    AddFavoriteResponseData,
    RemoveFavoriteResponse,
    RemoveFavoriteResponseData,
    SkipOutfitsRequest,
    SkipOutfitsResponse,
    SkipOutfitsResponseData,
)
from app.services.auth_service import get_user_from_token
from app.services.outfits_service import (
    add_favorite,
    get_favorite_outfits,
    get_outfits_list,
    remove_favorite,
    skip_outfits,
)

# 코디 목록 조회 관련 라우터(접두사: /outfits)
router = APIRouter(prefix="/outfits", tags=["Outfits"])

# 계절 필터 허용값
SeasonFilter = Literal["all", "spring", "summer", "fall", "winter"]

# 스타일 필터 허용값
StyleFilter = Literal["all", "casual", "street", "sporty", "minimal"]

# 성별 필터 허용값
GenderFilter = Literal["all", "male", "female"]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=RecommendationsResponse,
)
async def get_outfits(
    season: SeasonFilter = Query(default="all", description="계절 필터"),
    style: StyleFilter = Query(default="all", description="스타일 필터"),
    gender: GenderFilter = Query(default="all", description="성별 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=20, ge=1, le=50, description="페이지당 개수"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """
    필터링된 코디 목록을 조회합니다.
    
    season, style, gender로 필터링할 수 있으며, 여러 필터를 동시에 사용하면
    모든 조건을 만족하는 코디만 반환됩니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 코디 목록 조회
    outfits, pagination = await get_outfits_list(
        db=db,
        user_id=user.user_id,
        season=season,
        style=style,
        gender=gender,
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


@router.post(
    "/skip",
    status_code=status.HTTP_200_OK,
    response_model=SkipOutfitsResponse,
)
async def skip_outfits_endpoint(
    request: SkipOutfitsRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> SkipOutfitsResponse:
    """
    사용자가 본 코디들을 스킵으로 기록합니다.
    
    이미 좋아요로 기록된 코디는 스킵으로 변경되지 않습니다.
    이후 추천 API 호출 시 자동으로 제외됩니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 스킵 기록
    recorded_count, skipped_count = skip_outfits(
        db=db,
        user_id=user.user_id,
        coordi_ids=request.outfit_ids,
    )
    
    # 응답 메시지 생성
    message = f"{recorded_count}개의 코디가 스킵으로 기록되었습니다"
    
    # 응답 반환
    return SkipOutfitsResponse(
        data=SkipOutfitsResponseData(
            message=message,
            recordedCount=recorded_count,
            skippedCount=skipped_count,
        )
    )


@router.get(
    "/favorites",
    status_code=status.HTTP_200_OK,
    response_model=RecommendationsResponse,
)
async def get_favorite_outfits_endpoint(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=20, ge=1, le=50, description="페이지당 개수"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """
    사용자가 좋아요한 코디 목록을 조회합니다.
    
    좋아요 추가 일시 기준으로 최신순으로 정렬됩니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 좋아요한 코디 목록 조회
    outfits, pagination = await get_favorite_outfits(
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


@router.post(
    "/{outfit_id}/favorite",
    status_code=status.HTTP_200_OK,
    response_model=AddFavoriteResponse,
)
async def add_favorite_endpoint(
    outfit_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> AddFavoriteResponse:
    """
    코디에 좋아요를 추가합니다.
    
    이미 좋아요한 코디에 다시 좋아요를 추가할 수 없습니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 좋아요 추가
    interaction = add_favorite(
        db=db,
        user_id=user.user_id,
        coordi_id=outfit_id,
    )
    
    # 응답 반환
    return AddFavoriteResponse(
        data=AddFavoriteResponseData(
            outfitId=interaction.coordi_id,
            isFavorited=True,
            favoritedAt=interaction.interacted_at,
        )
    )


@router.delete(
    "/{outfit_id}/favorite",
    status_code=status.HTTP_200_OK,
    response_model=RemoveFavoriteResponse,
)
async def remove_favorite_endpoint(
    outfit_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> RemoveFavoriteResponse:
    """
    코디 좋아요를 취소합니다.
    
    좋아요하지 않은 코디에 대해 취소 요청을 할 수 없습니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 좋아요 취소
    coordi_id, unfavorited_at = remove_favorite(
        db=db,
        user_id=user.user_id,
        coordi_id=outfit_id,
    )
    
    # 응답 반환
    return RemoveFavoriteResponse(
        data=RemoveFavoriteResponseData(
            outfitId=coordi_id,
            isFavorited=False,
            unfavoritedAt=unfavorited_at,
        )
    )

