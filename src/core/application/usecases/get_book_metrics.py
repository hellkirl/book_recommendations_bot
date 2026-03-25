from core.domain.model.rating_metrics import BookRatingMetrics
from core.ports.rating_repository import IRatingRepository


class GetBookMetricsUseCase:
    def __init__(self, ratings_repo: IRatingRepository) -> None:
        self._repo = ratings_repo

    def execute(self, book_id: int) -> BookRatingMetrics:
        return self._repo.get_book_metrics(book_id)

