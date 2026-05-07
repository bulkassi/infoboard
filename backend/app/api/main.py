from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.boards import router as boards_router
from app.api.routes.cards import router as cards_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.share_links import router as share_links_router
from app.api.routes.tags import router as tags_router
from app.api.routes.users import router as users_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(boards_router, tags=["boards"])
api_router.include_router(cards_router, tags=["cards"])
api_router.include_router(tags_router, tags=["tags"])
api_router.include_router(files_router, tags=["files"])
api_router.include_router(share_links_router, tags=["share-links"])
