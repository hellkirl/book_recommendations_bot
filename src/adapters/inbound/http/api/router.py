from fastapi import APIRouter

from .routes import popular, similar, search, recommend, ratings

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(
    popular.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(
    similar.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(
    search.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(
    recommend.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(ratings.router, tags=["ratings"])
