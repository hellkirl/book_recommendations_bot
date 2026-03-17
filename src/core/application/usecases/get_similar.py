from core.domain.model.book import BookRecommendation
from core.ports.recommendation_service import IContentService
from core.ports.rating_repository import IRatingRepository


class GetSimilarUseCase:
    def __init__(
        self, content: IContentService, ratings_repo: IRatingRepository
    ) -> None:
        self._content = content
        self._ratings_repo = ratings_repo

    def execute(
        self,
        book_id: int,
        telegram_id: int | None = None,
        n: int = 10,
    ) -> list[BookRecommendation]:
        exclude = (
            self._ratings_repo.get_rated_book_ids(telegram_id) if telegram_id else set()
        )
        return self._content.get_similar_by_book(
            book_id=book_id, n=n, exclude_books=exclude
        )
