from dataclasses import dataclass
from datetime import datetime


@dataclass
class Rating:
    telegram_id: int
    book_id: int
    score: int
    created_at: datetime = None

    def __post_init__(self):
        if not (1 <= self.score <= 5):
            raise ValueError(f"score must be between 1 and 5, got {self.score}")
        if self.created_at is None:
            self.created_at = datetime.now()
