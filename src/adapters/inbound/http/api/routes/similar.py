from fastapi import APIRouter, Depends, Query

from adapters.inbound.http.api.dependencies import get_similar_uc
from adapters.inbound.http.api.schemas import Book, RecommendationResponse
from core.application.usecases.get_similar import GetSimilarUseCase

router = APIRouter()


@router.get("/similar/{book_id}", response_model=RecommendationResponse)
def get_similar(
    book_id: int,
    telegram_id: int | None = Query(None, description="Exclude already-read books"),
    n: int = Query(10, ge=1, le=50),
    uc: GetSimilarUseCase = Depends(get_similar_uc),
):
    books = uc.execute(book_id=book_id, telegram_id=telegram_id, n=n)
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
