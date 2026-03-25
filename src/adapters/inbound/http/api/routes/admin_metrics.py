from fastapi import APIRouter, Depends

from adapters.inbound.http.api.dependencies import (
    get_book_interaction_metrics_uc,
    get_book_metrics_uc,
)
from adapters.inbound.http.api.schemas import BookRatingMetricsResponse
from core.application.usecases.get_book_metrics import GetBookMetricsUseCase
from core.application.usecases.get_book_interaction_metrics import (
    GetBookInteractionMetricsUseCase,
)

router = APIRouter()


@router.get(
    "/admin/metrics/books/{book_id}",
    response_model=BookRatingMetricsResponse,
    tags=["admin"],
)
def get_book_metrics(
    book_id: int,
    uc: GetBookMetricsUseCase = Depends(get_book_metrics_uc),
    interactions_uc: GetBookInteractionMetricsUseCase = Depends(
        get_book_interaction_metrics_uc
    ),
):
    metrics = uc.execute(book_id=book_id)
    interactions = interactions_uc.execute(book_id=book_id)
    return BookRatingMetricsResponse(
        book_id=metrics.book_id,
        rating_count=metrics.rating_count,
        rating_mean=metrics.rating_mean,
        ratings_by_score=metrics.ratings_by_score,
        impressions_count=interactions.impressions_count,
        clicks_count=interactions.clicks_count,
    )

