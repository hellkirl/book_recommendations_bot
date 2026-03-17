from fastapi import APIRouter, Depends

from adapters.inbound.http.api.dependencies import get_save_rating_uc
from adapters.inbound.http.api.schemas import RatingRequest, RatingResponse
from core.application.usecases.save_rating import SaveRatingUseCase

router = APIRouter()


@router.post("/ratings", response_model=RatingResponse)
def save_rating(
    body: RatingRequest,
    uc: SaveRatingUseCase = Depends(get_save_rating_uc),
):
    unlocked = uc.execute(
        telegram_id=body.telegram_id,
        book_id=body.book_id,
        score=body.score,
    )
    return RatingResponse(unlocked_personal=unlocked)
