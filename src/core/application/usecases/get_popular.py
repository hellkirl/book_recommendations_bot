from core.domain.model.book import BookRecommendation
from core.ports.recommendation_service import IPopularityService
from core.ports.rating_repository import IRatingRepository


class GetPopularUseCase:
    def __init__(
        self, popularity: IPopularityService, ratings_repo: IRatingRepository
    ) -> None:
        self._popularity = popularity
        self._ratings_repo = ratings_repo

    def execute(
        self,
        mode: str,
        telegram_id: int | None = None,
        genre: str | None = None,
        n: int = 10,
    ) -> list[BookRecommendation]:
        exclude = (
            self._ratings_repo.get_rated_book_ids(telegram_id) if telegram_id else set()
        )
        return self._popularity.get_popular(
            mode=mode, n=n, genre=genre, exclude_books=exclude
        )
