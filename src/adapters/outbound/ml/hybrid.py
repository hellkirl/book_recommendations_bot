import numpy as np

from core.domain.model.book import BookRecommendation
from core.domain.model.rating import Rating
from core.ports.recommendation_service import IHybridService
from .content_based import ContentService
from .collaborative import CollaborativeService


def _normalize(scores: list[float]) -> list[float]:
    arr = np.array(scores, dtype=float)
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return [1.0] * len(scores)
    return ((arr - mn) / (mx - mn)).tolist()


class HybridService(IHybridService):
    def __init__(self) -> None:
        self._content = ContentService()
        self._collab = CollaborativeService()

    def get_hybrid(
        self,
        ratings: list[Rating],
        n: int = 10,
        cb_weight: float = 0.5,
        als_weight: float = 0.5,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]:
        fetch = n * 3

        als_results = self._collab.get_personal(
            ratings, n=fetch, exclude_books=exclude_books
        )

        best = max(ratings, key=lambda r: r.score, default=None)
        cb_results = (
            self._content.get_similar_by_book(
                best.book_id, n=fetch, exclude_books=exclude_books
            )
            if best
            else []
        )

        als_map: dict[int, float] = {}
        if als_results:
            normed = _normalize([b.score for b in als_results])
            als_map = {b.book_id: s for b, s in zip(als_results, normed)}

        cb_map: dict[int, float] = {}
        if cb_results:
            normed = _normalize([b.score for b in cb_results])
            cb_map = {b.book_id: s for b, s in zip(cb_results, normed)}

        all_candidates: dict[int, BookRecommendation] = {
            b.book_id: b for b in (*als_results, *cb_results)
        }

        scored: list[tuple[float, BookRecommendation]] = []
        for book_id, book in all_candidates.items():
            hybrid_score = als_weight * als_map.get(
                book_id, 0.0
            ) + cb_weight * cb_map.get(book_id, 0.0)
            scored.append((hybrid_score, book))

        scored.sort(key=lambda x: x[0], reverse=True)

        results: list[BookRecommendation] = []
        seen_titles: set[str] = set()
        for hybrid_score, book in scored:
            if book.title in seen_titles:
                continue
            seen_titles.add(book.title)
            book.score = hybrid_score
            results.append(book)
            if len(results) == n:
                break

        return results
