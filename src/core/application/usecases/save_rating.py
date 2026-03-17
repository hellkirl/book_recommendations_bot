from core.domain.model.rating import Rating
from core.ports.rating_repository import IRatingRepository

PERSONAL_THRESHOLD = 10


class SaveRatingUseCase:
    def __init__(self, ratings_repo: IRatingRepository) -> None:
        self._repo = ratings_repo

    def execute(self, telegram_id: int, book_id: int, score: int) -> bool:
        was_below = self._repo.count_ratings(telegram_id) < PERSONAL_THRESHOLD
        self._repo.save_rating(
            Rating(telegram_id=telegram_id, book_id=book_id, score=score)
        )
        now_at_or_above = self._repo.count_ratings(telegram_id) >= PERSONAL_THRESHOLD
        return was_below and now_at_or_above
