from fastapi import APIRouter, Depends, Query

from adapters.inbound.http.api.dependencies import get_search_uc
from adapters.inbound.http.api.schemas import Book, RecommendationResponse
from core.application.usecases.search_by_query import SearchByQueryUseCase

router = APIRouter()


@router.get("/search", response_model=RecommendationResponse)
def search(
    q: str = Query(
        ...,
        min_length=1,
        description="Free-text query, e.g. 'детектив в викторианской Англии'",
    ),
    n: int = Query(10, ge=1, le=50),
    uc: SearchByQueryUseCase = Depends(get_search_uc),
):
    books = uc.execute(query=q, n=n)
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
