import logging

from fastapi import APIRouter, Depends

from adapters.inbound.http.api.dependencies import get_book_metrics_uc, get_save_rating_uc
from adapters.inbound.http.api.schemas import RatingRequest, RatingResponse
from core.application.usecases.get_book_metrics import GetBookMetricsUseCase
from core.application.usecases.save_rating import SaveRatingUseCase

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/ratings", response_model=RatingResponse)
def save_rating(
    body: RatingRequest,
    uc: SaveRatingUseCase = Depends(get_save_rating_uc),
    metrics_uc: GetBookMetricsUseCase = Depends(get_book_metrics_uc),
):
    unlocked = uc.execute(
        telegram_id=body.telegram_id,
        book_id=body.book_id,
        score=body.score,
    )
    metrics = metrics_uc.execute(book_id=body.book_id)
    logger.info(
        "METRICS book_rating_saved telegram_id=%s book_id=%s score=%s rating_count=%s rating_mean=%s ratings_by_score=%s",
        body.telegram_id,
        body.book_id,
        body.score,
        metrics.rating_count,
        metrics.rating_mean,
        metrics.ratings_by_score,
    )
    return RatingResponse(unlocked_personal=unlocked)
