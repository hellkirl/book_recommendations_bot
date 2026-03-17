import pandas as pd

from core.domain.model.book import BookRecommendation
from core.ports.recommendation_service import IPopularityService
from .model_loader import get_artifacts


def _row_to_book(row: pd.Series, score: float) -> BookRecommendation:
    return BookRecommendation(
        book_id=int(row["book_id"]),
        title=str(row["title"]),
        author=str(row.get("authors_str", "")),
        genre=str(row["genres_str"]) if pd.notna(row.get("genres_str")) else None,
        rating_mean=float(row.get("rating_mean", 0.0)),
        rating_count=int(row.get("rating_count", 0)),
        score=score,
    )


class PopularityService(IPopularityService):
    def get_popular(
        self,
        mode: str,
        n: int = 10,
        genre: str | None = None,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]:
        arts = get_artifacts()

        if mode == "gold":
            df = arts.pop_gold
            score_col = "bayesian_score"

        elif mode == "trends":
            df = arts.pop_trends
            score_col = "trend_score"

        elif mode == "genre":
            if not genre:
                raise ValueError("genre is required when mode='genre'")
            df = arts.pop_by_genre[arts.pop_by_genre["genre"] == genre]
            score_col = "bayesian_score"

        else:
            raise ValueError(f"Unknown popularity mode: {mode!r}")

        if exclude_books:
            df = df[~df["book_id"].isin(exclude_books)]

        df = df.drop_duplicates(subset="book_id")
        df = df.drop_duplicates(subset="title")

        top = df.nlargest(n, score_col)
        return [_row_to_book(row, float(row[score_col])) for _, row in top.iterrows()]
