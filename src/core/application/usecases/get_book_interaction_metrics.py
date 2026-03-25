from core.domain.model.book_interaction_metrics import BookInteractionMetrics
from core.ports.book_interaction_repository import IBookInteractionRepository


class GetBookInteractionMetricsUseCase:
    def __init__(self, interactions_repo: IBookInteractionRepository) -> None:
        self._repo = interactions_repo

    def execute(self, book_id: int) -> BookInteractionMetrics:
        return self._repo.get_book_interaction_metrics(book_id)

