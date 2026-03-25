from pydantic import BaseModel, Field


class Book(BaseModel):
    book_id: int
    title: str
    author: str
    genre: str | None = None
    score: float | None = None


class RecommendationResponse(BaseModel):
    books: list[Book]


class RatingRequest(BaseModel):
    telegram_id: int
    book_id: int
    score: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    unlocked_personal: bool


class BookRatingMetricsResponse(BaseModel):
    book_id: int
    rating_count: int
    rating_mean: float
    ratings_by_score: dict[int, int]
