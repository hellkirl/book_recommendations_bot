from fastapi import APIRouter, Depends, Query

from adapters.inbound.http.api.dependencies import get_recommendations_uc
from adapters.inbound.http.api.schemas import Book, RecommendationResponse
from core.application.usecases.get_recommendations import GetRecommendationsUseCase

router = APIRouter()


@router.get("/personal/{telegram_id}", response_model=RecommendationResponse)
def get_personal(
    telegram_id: int,
    n: int = Query(10, ge=1, le=50),
    uc: GetRecommendationsUseCase = Depends(get_recommendations_uc),
):
    books = uc.execute(telegram_id=telegram_id, n=n)
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
