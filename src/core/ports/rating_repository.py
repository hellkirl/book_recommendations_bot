from abc import ABC, abstractmethod

from core.domain.model.rating import Rating
from core.domain.model.rating_metrics import BookRatingMetrics


class IRatingRepository(ABC):

    @abstractmethod
    def get_ratings(self, telegram_id: int) -> list[Rating]: ...

    @abstractmethod
    def save_rating(self, rating: Rating) -> None: ...

    @abstractmethod
    def count_ratings(self, telegram_id: int) -> int: ...

    @abstractmethod
    def get_rated_book_ids(self, telegram_id: int) -> set[int]: ...

    @abstractmethod
    def get_book_metrics(self, book_id: int) -> BookRatingMetrics: ...
