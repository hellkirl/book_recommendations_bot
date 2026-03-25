from dataclasses import dataclass


@dataclass(frozen=True)
class BookInteractionMetrics:
    book_id: int
    impressions_count: int
    clicks_count: int

