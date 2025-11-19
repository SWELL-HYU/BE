from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.api.recommendations import router as recommendations_router
from app.api.users import router as users_router

api_router = APIRouter()

# 인증 관련 라우터
api_router.include_router(auth_router)

# 아이템 관련 라우터
api_router.include_router(items_router)

# 사용자 관련 라우터
api_router.include_router(users_router)

# 코디 추천 관련 라우터
api_router.include_router(recommendations_router)

__all__ = ["api_router"]


