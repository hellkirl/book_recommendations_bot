import numpy as np
import pandas as pd

import config
from core.domain.model.book import BookRecommendation
from core.domain.model.rating import Rating
from core.ports.recommendation_service import ICollaborativeService
from .model_loader import get_artifacts


def _fold_in_user(
    item_factors: np.ndarray,
    rated_indices: list[int],
    confidences: list[float],
    regularization: float,
) -> np.ndarray:
    Y = item_factors[rated_indices]
    c = np.array(confidences, dtype=np.float32)
    n_factors = item_factors.shape[1]

    YtCY = (Y.T @ (Y * c[:, None])) + regularization * np.eye(
        n_factors, dtype=np.float32
    )
    YtCp = Y.T @ c
    return np.linalg.solve(YtCY, YtCp).astype(np.float32)


class CollaborativeService(ICollaborativeService):
    def get_personal(
        self,
        ratings: list[Rating],
        n: int = 10,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]:
        arts = get_artifacts()

        rated_indices: list[int] = []
        confidences: list[float] = []
        for r in ratings:
            idx = arts.als_reverse_book_map.get(r.book_id)
            if idx is not None and idx < arts.item_factors.shape[0]:
                rated_indices.append(idx)
                confidences.append(config.ALS_ALPHA * float(r.score))

        if not rated_indices:
            return []

        user_factor = _fold_in_user(
            arts.item_factors, rated_indices, confidences, config.ALS_REGULARIZATION
        )

        all_scores = arts.item_factors @ user_factor
        order = np.argsort(all_scores)[::-1]

        rated_set = set(rated_indices)
        exclude_als_idxs = {
            arts.als_reverse_book_map[b]
            for b in exclude_books
            if b in arts.als_reverse_book_map
        }

        results: list[BookRecommendation] = []
        seen_titles: set[str] = set()
        for als_idx in order:
            if als_idx in rated_set or als_idx in exclude_als_idxs:
                continue
            book_id = arts.als_book_id_map.get(int(als_idx))
            if book_id is None:
                continue
            cb_idx = arts.book_id_to_cb_idx.get(book_id)
            if cb_idx is not None:
                row = arts.cb_meta.iloc[cb_idx]
                genre = (
                    str(row["genres_str"]) if pd.notna(row.get("genres_str")) else None
                )
                title = str(row["title"])
            else:
                row = None
                genre = None
                title = f"Book {book_id}"
            if title in seen_titles:
                continue
            seen_titles.add(title)
            results.append(
                BookRecommendation(
                    book_id=book_id,
                    title=title,
                    author="",
                    genre=genre,
                    rating_mean=0.0,
                    rating_count=0,
                    score=float(all_scores[als_idx]),
                )
            )
            if len(results) == n:
                break

        return results
