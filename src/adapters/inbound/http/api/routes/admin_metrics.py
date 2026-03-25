from fastapi import APIRouter, Depends

from adapters.inbound.http.api.dependencies import get_book_metrics_uc
from adapters.inbound.http.api.schemas import BookRatingMetricsResponse
from core.application.usecases.get_book_metrics import GetBookMetricsUseCase

router = APIRouter()


@router.get(
    "/admin/metrics/books/{book_id}",
    response_model=BookRatingMetricsResponse,
    tags=["admin"],
)
def get_book_metrics(
    book_id: int,
    uc: GetBookMetricsUseCase = Depends(get_book_metrics_uc),
):
    metrics = uc.execute(book_id=book_id)
    return BookRatingMetricsResponse(
        book_id=metrics.book_id,
        rating_count=metrics.rating_count,
        rating_mean=metrics.rating_mean,
        ratings_by_score=metrics.ratings_by_score,
    )

