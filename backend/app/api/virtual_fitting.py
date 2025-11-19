"""
가상 피팅 관련 API 라우터.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.security import extract_bearer_token
from app.db.database import get_db
from app.schemas.user_request import VirtualFittingRequest
from app.schemas.user_response import (
    DeleteFittingHistoryResponse,
    FittingHistoryResponse,
    VirtualFittingJobStatusResponse,
    VirtualFittingResponse,
)
from app.services.auth_service import get_user_from_token
from app.services.virtual_fitting_service import (
    _process_virtual_fitting_async,
    delete_virtual_fitting_history,
    get_virtual_fitting_history,
    get_virtual_fitting_status,
    start_virtual_fitting,
)


def _process_virtual_fitting_with_new_session(
    fitting_id: int,
    user_id: int,
    items,
) -> None:
    """
    새로운 DB 세션을 생성하여 가상 피팅 처리를 수행합니다.
    백그라운드 작업에서 호출됩니다.
    """
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        import asyncio
        asyncio.run(
            _process_virtual_fitting_async(
                db=db,
                fitting_id=fitting_id,
                user_id=user_id,
                items=items,
            )
        )
    finally:
        db.close()

router = APIRouter(prefix="/virtual-fitting", tags=["Virtual Fitting"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=FittingHistoryResponse,
)
async def get_virtual_fitting_history_endpoint(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=20, ge=1, le=50, description="페이지당 개수"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> FittingHistoryResponse:
    """
    가상 피팅 이력을 조회합니다.
    
    현재 로그인한 사용자의 가상 피팅 이력을 최신순으로 반환합니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 가상 피팅 이력 조회
    history_data = get_virtual_fitting_history(
        db=db,
        user_id=user.user_id,
        page=page,
        limit=limit,
    )
    
    # 응답 반환
    return FittingHistoryResponse(
        data=history_data,
    )


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=VirtualFittingResponse,
)
async def start_virtual_fitting_endpoint(
    request: VirtualFittingRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> VirtualFittingResponse:
    """
    가상 피팅 작업을 시작합니다.
    
    비동기로 처리되며, 즉시 결과를 반환하지 않습니다.
    결과는 별도의 조회 API를 통해 확인할 수 있습니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 가상 피팅 작업 시작
    # 유효성 검증, 예외 처리, 기본 레코드 생성 등 필요한 작업을 수행
    fitting_id = start_virtual_fitting(
        db=db,
        user_id=user.user_id,
        request=request,
    )
    
    # 백그라운드 작업으로 피팅 처리 시작
    # 주의: 백그라운드 작업은 별도 스레드에서 실행되므로 새로운 DB 세션을 생성해야 함
    # 실제 피팅 처리는 백그라운드에서 실행되며, 클라이언트는 즉시 응답을 받음
    # 작업 완료 여부는 별도의 조회 API를 통해 확인할 수 있음.
    background_tasks.add_task(
        _process_virtual_fitting_with_new_session,
        fitting_id=fitting_id,
        user_id=user.user_id,
        items=request.items,
    )
    
    # FittingResult 조회 (created_at 포함)
    from app.models.fitting_result import FittingResult
    fitting_result = db.get(FittingResult, fitting_id)
    
    # 응답 반환
    return VirtualFittingResponse(
        data={
            "jobId": fitting_id,
            "status": fitting_result.status,
            "createdAt": fitting_result.created_at,
        }
    )


@router.get(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=VirtualFittingJobStatusResponse,
)
async def get_virtual_fitting_status_endpoint(
    job_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> VirtualFittingJobStatusResponse:
    """
    가상 피팅 작업의 상태를 조회합니다.
    
    작업 상태에 따라 다른 응답 구조를 반환합니다:
    - processing: 현재 처리 단계 정보
    - completed: 결과 이미지, LLM 메시지, 처리 시간
    - failed: 에러 메시지, 실패한 단계
    - timeout: 타임아웃 메시지
    
    클라이언트는 2초 간격으로 폴링하는 것을 권장합니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 가상 피팅 상태 조회
    status_payload = get_virtual_fitting_status(
        db=db,
        fitting_id=job_id,
        user_id=user.user_id,
    )
    
    # 응답 반환
    return VirtualFittingJobStatusResponse(
        data=status_payload,
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteFittingHistoryResponse,
)
async def delete_virtual_fitting_history_endpoint(
    job_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> DeleteFittingHistoryResponse:
    """
    가상 피팅 이력을 삭제합니다.
    
    현재 로그인한 사용자가 생성한 가상 피팅 작업만 삭제할 수 있습니다.
    삭제된 이력은 복구할 수 없으며, 관련된 모든 데이터가 함께 삭제됩니다.
    """
    # 헤더에서 토큰 추출
    token = extract_bearer_token(authorization)
    
    # 토큰 검증 및 사용자 조회
    user = get_user_from_token(db, token)
    
    # 가상 피팅 이력 삭제
    deleted_at = delete_virtual_fitting_history(
        db=db,
        fitting_id=job_id,
        user_id=user.user_id,
    )
    
    # 응답 반환
    return DeleteFittingHistoryResponse(
        data={
            "message": "가상 피팅 이력이 삭제되었습니다",
            "deletedAt": deleted_at,
        }
    )

