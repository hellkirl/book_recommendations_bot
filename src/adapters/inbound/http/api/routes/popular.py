from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.inbound.http.api.dependencies import get_popular_uc
from adapters.inbound.http.api.schemas import Book, RecommendationResponse
from core.application.usecases.get_popular import GetPopularUseCase

router = APIRouter()

VALID_MODES = {"gold", "trends", "genre"}


@router.get("/popular", response_model=RecommendationResponse)
def get_popular(
    mode: str = Query("gold", description="gold | trends | genre"),
    genre: str | None = Query(None, description="Required when mode=genre"),
    telegram_id: int | None = Query(None, description="Exclude already-read books"),
    n: int = Query(10, ge=1, le=50),
    uc: GetPopularUseCase = Depends(get_popular_uc),
):
    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400, detail=f"mode must be one of {VALID_MODES}"
        )
    if mode == "genre" and not genre:
        raise HTTPException(status_code=400, detail="genre is required when mode=genre")

    books = uc.execute(mode=mode, telegram_id=telegram_id, genre=genre, n=n)
    return RecommendationResponse(
        books=[
            Book(
                book_id=b.book_id,
                title=b.title,
                author=b.author,
                genre=b.genre,
                score=b.score,
            )
            for b in books
        ]
    )
