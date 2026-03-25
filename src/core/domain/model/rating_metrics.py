from dataclasses import dataclass


@dataclass(frozen=True)
class BookRatingMetrics:
    book_id: int
    rating_count: int
    rating_mean: float
    ratings_by_score: dict[int, int]

