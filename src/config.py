import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "trained"

POP_GOLD_PATH = MODELS_DIR / "mostpop" / "popularity_gold.csv"
POP_TRENDS_PATH = MODELS_DIR / "mostpop" / "popularity_trends.csv"
POP_BY_GENRE_PATH = MODELS_DIR / "mostpop" / "popularity_by_genre.csv"
TOP_GENRES_PATH = MODELS_DIR / "mostpop" / "top_genres.csv"

CB_ASSETS_PATH = MODELS_DIR / "cb" / "cb_assets.pkl"
EMBEDDINGS_PATH = MODELS_DIR / "cb" / "embeddings.npy"
FAISS_INDEX_PATH = MODELS_DIR / "cb" / "books_index.faiss"

ALS_MODEL_PATH = MODELS_DIR / "hybrid" / "als_model.npz"
ALS_MAPPINGS_PATH = MODELS_DIR / "hybrid" / "als_mappings.pkl"

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

ALS_REGULARIZATION = 0.05
ALS_ALPHA = 1.0

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot.db")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
