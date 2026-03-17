import numpy as np
import pandas as pd

from core.domain.model.book import BookRecommendation
from core.ports.recommendation_service import IContentService
from .model_loader import ModelArtifacts, get_artifacts


def _meta_to_book(row: pd.Series, score: float) -> BookRecommendation:
    return BookRecommendation(
        book_id=int(row["book_id"]),
        title=str(row["title"]),
        author="",
        genre=str(row["genres_str"]) if pd.notna(row.get("genres_str")) else None,
        rating_mean=0.0,
        rating_count=0,
        score=score,
    )


def _faiss_search(
    arts: ModelArtifacts,
    query_vec: np.ndarray,
    n: int,
    exclude_book_ids: set[int],
    skip_cb_idx: int | None = None,
    genre_filter: str | None = None,
) -> list[BookRecommendation]:
    base_k = 1000 if genre_filter else 100
    k = min(n + len(exclude_book_ids) + base_k, arts.faiss_index.ntotal)
    q = query_vec.reshape(1, -1).astype("float32")
    distances, indices = arts.faiss_index.search(q, k)

    results: list[BookRecommendation] = []
    seen_titles: set[str] = set()
    for cb_idx, dist in zip(indices[0], distances[0]):
        if cb_idx < 0 or cb_idx == skip_cb_idx:
            continue
        book_id = arts.cb_idx_to_book_id.get(int(cb_idx))
        if book_id is None or book_id in exclude_book_ids:
            continue
        row = arts.cb_meta.iloc[cb_idx]
        title = str(row["title"])
        if title in seen_titles:
            continue
        if genre_filter:
            genres = str(row.get("genres_str", "")).lower()
            if genre_filter.lower() not in genres:
                continue
        seen_titles.add(title)
        results.append(_meta_to_book(row, score=float(dist)))
        if len(results) == n:
            break

    return results


class ContentService(IContentService):
    def get_similar_by_book(
        self,
        book_id: int,
        n: int = 10,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]:
        arts = get_artifacts()
        cb_idx = arts.book_id_to_cb_idx.get(book_id)
        if cb_idx is None:
            return []
        query_vec = arts.embeddings[cb_idx]
        return _faiss_search(arts, query_vec, n, exclude_books, skip_cb_idx=cb_idx)

    def get_similar_by_query(
        self,
        query: str,
        n: int = 10,
        genre_filter: str | None = None,
        exclude_books: set[int] = frozenset(),
    ) -> list[BookRecommendation]:
        arts = get_artifacts()
        query_vec = arts.encoder.encode(query, normalize_embeddings=True)
        return _faiss_search(
            arts, query_vec, n, exclude_books, genre_filter=genre_filter
        )
