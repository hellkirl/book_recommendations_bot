from abc import ABC, abstractmethod

from core.domain.model.book import BookRecommendation
from core.domain.model.rating import Rating


class IPopularityService(ABC):
    @abstractmethod
    def get_popular(
        self,
        mode: str,
        n: int = 10,
        genre: str | None = None,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]: ...


class IContentService(ABC):
    @abstractmethod
    def get_similar_by_book(
        self,
        book_id: int,
        n: int = 10,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]: ...

    @abstractmethod
    def get_similar_by_query(
        self,
        query: str,
        n: int = 10,
        genre_filter: str | None = None,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]: ...


class ICollaborativeService(ABC):
    @abstractmethod
    def get_personal(
        self,
        ratings: list[Rating],
        n: int = 10,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]: ...


class IHybridService(ABC):
    @abstractmethod
    def get_hybrid(
        self,
        ratings: list[Rating],
        n: int = 10,
        cb_weight: float = 0.5,
        als_weight: float = 0.5,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]: ...
