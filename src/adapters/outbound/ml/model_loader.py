import os
import pickle
from dataclasses import dataclass

import config

os.environ.setdefault("HF_HOME", str(config.MODELS_DIR / "hf_home"))
os.environ.setdefault(
    "TRANSFORMERS_CACHE", str(config.MODELS_DIR / "hf_home" / "transformers")
)
if config.HF_TOKEN:
    os.environ.setdefault("HF_TOKEN", config.HF_TOKEN)

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


@dataclass
class ModelArtifacts:
    pop_gold: pd.DataFrame
    pop_trends: pd.DataFrame
    pop_by_genre: pd.DataFrame
    top_genres: list[str]

    cb_meta: pd.DataFrame
    book_id_to_cb_idx: dict
    cb_idx_to_book_id: dict
    embeddings: np.ndarray
    faiss_index: faiss.Index
    encoder: SentenceTransformer

    item_factors: np.ndarray
    als_book_id_map: dict
    als_reverse_book_map: dict


_artifacts: ModelArtifacts | None = None


def get_artifacts() -> ModelArtifacts:
    global _artifacts
    if _artifacts is None:
        _artifacts = _load()
    return _artifacts


def _load() -> ModelArtifacts:
    pop_gold = pd.read_csv(config.POP_GOLD_PATH)
    pop_trends = pd.read_csv(config.POP_TRENDS_PATH)
    pop_by_genre = pd.read_csv(config.POP_BY_GENRE_PATH)

    tg_df = pd.read_csv(config.TOP_GENRES_PATH)
    top_genres = [tg_df.columns[0]] + tg_df.iloc[:, 0].tolist()

    with open(config.CB_ASSETS_PATH, "rb") as f:
        cb_assets = pickle.load(f)

    cb_meta = cb_assets["metadata"]
    book_id_to_cb_idx = {int(k): int(v) for k, v in cb_assets["book_id_to_idx"].items()}
    cb_idx_to_book_id = {int(k): int(v) for k, v in cb_assets["idx_to_book_id"].items()}

    embeddings = np.load(config.EMBEDDINGS_PATH)
    faiss_index = faiss.read_index(str(config.FAISS_INDEX_PATH))

    encoder = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

    als_data = np.load(config.ALS_MODEL_PATH, allow_pickle=True)
    item_factors = als_data["item_factors"].astype(np.float32)

    with open(config.ALS_MAPPINGS_PATH, "rb") as f:
        mappings = pickle.load(f)

    als_book_id_map = {int(k): int(v) for k, v in mappings["book_id_map"].items()}
    als_reverse_book_map = {
        int(k): int(v) for k, v in mappings["reverse_book_map"].items()
    }

    return ModelArtifacts(
        pop_gold=pop_gold,
        pop_trends=pop_trends,
        pop_by_genre=pop_by_genre,
        top_genres=top_genres,
        cb_meta=cb_meta,
        book_id_to_cb_idx=book_id_to_cb_idx,
        cb_idx_to_book_id=cb_idx_to_book_id,
        embeddings=embeddings,
        faiss_index=faiss_index,
        encoder=encoder,
        item_factors=item_factors,
        als_book_id_map=als_book_id_map,
        als_reverse_book_map=als_reverse_book_map,
    )
