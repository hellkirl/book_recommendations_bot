from abc import ABC, abstractmethod

from core.domain.model.book_interaction_metrics import BookInteractionMetrics


class IBookInteractionRepository(ABC):
    @abstractmethod
    def record_impression(
        self, book_id: int, telegram_id: int | None = None
    ) -> None: ...

    @abstractmethod
    def record_click(self, book_id: int, telegram_id: int | None = None) -> None: ...

    @abstractmethod
    def get_book_interaction_metrics(self, book_id: int) -> BookInteractionMetrics: ...

