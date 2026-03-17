from dataclasses import dataclass


@dataclass
class BookRecommendation:
    book_id: int
    title: str
    author: str
    genre: str | None
    rating_mean: float
    rating_count: int
    score: float
