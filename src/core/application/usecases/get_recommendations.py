from core.domain.model.book import BookRecommendation
from core.domain.model.rating import Rating
from core.ports.recommendation_service import (
    IPopularityService,
    IContentService,
    IHybridService,
)
from core.ports.rating_repository import IRatingRepository


class GetRecommendationsUseCase:
    def __init__(
        self,
        ratings_repo: IRatingRepository,
        popularity: IPopularityService,
        content: IContentService,
        hybrid: IHybridService,
    ) -> None:
        self._repo = ratings_repo
        self._popularity = popularity
        self._content = content
        self._hybrid = hybrid

    def execute(self, telegram_id: int, n: int = 10) -> list[BookRecommendation]:
        ratings = self._repo.get_ratings(telegram_id)
        exclude = {r.book_id for r in ratings}
        count = len(ratings)

        if count == 0:
            return self._popularity.get_popular(mode="gold", n=n, exclude_books=exclude)

        if count <= 3:
            genre = _top_genre(ratings)
            if genre:
                return self._popularity.get_popular(
                    mode="genre", genre=genre, n=n, exclude_books=exclude
                )
            return self._popularity.get_popular(mode="gold", n=n, exclude_books=exclude)

        if count <= 9:
            best = max(ratings, key=lambda r: r.score)
            return self._content.get_similar_by_book(
                book_id=best.book_id, n=n, exclude_books=exclude
            )

        if count <= 24:
            return self._hybrid.get_hybrid(
                ratings=ratings,
                n=n,
                cb_weight=0.7,
                als_weight=0.3,
                exclude_books=exclude,
            )

        return self._hybrid.get_hybrid(
            ratings=ratings, n=n, cb_weight=0.4, als_weight=0.6, exclude_books=exclude
        )


def _top_genre(ratings: list[Rating]) -> str | None:
    import pandas as pd
    from adapters.outbound.ml.model_loader import get_artifacts

    arts = get_artifacts()
    liked_ids = {r.book_id for r in ratings if r.score >= 4} or {
        r.book_id for r in ratings
    }

    genres_series = arts.cb_meta.loc[
        arts.cb_meta["book_id"].isin(liked_ids), "genres_str"
    ].dropna()

    all_genres = " ".join(genres_series).split()
    valid = [g for g in all_genres if g in arts.top_genres]
    if not valid:
        return None
    return pd.Series(valid).value_counts().index[0]
