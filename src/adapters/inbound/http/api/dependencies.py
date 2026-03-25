from functools import lru_cache

from adapters.outbound.ml.popularity import PopularityService
from adapters.outbound.ml.content_based import ContentService
from adapters.outbound.ml.collaborative import CollaborativeService
from adapters.outbound.ml.hybrid import HybridService
from adapters.outbound.postgres.user_repository.repository import RatingRepository

from core.application.usecases.get_popular import GetPopularUseCase
from core.application.usecases.get_similar import GetSimilarUseCase
from core.application.usecases.search_by_query import SearchByQueryUseCase
from core.application.usecases.get_recommendations import GetRecommendationsUseCase
from core.application.usecases.get_book_metrics import GetBookMetricsUseCase
from core.application.usecases.save_rating import SaveRatingUseCase


@lru_cache(maxsize=1)
def _services():
    return dict(
        popularity=PopularityService(),
        content=ContentService(),
        collaborative=CollaborativeService(),
        hybrid=HybridService(),
        repo=RatingRepository(),
    )


def get_popular_uc() -> GetPopularUseCase:
    s = _services()
    return GetPopularUseCase(popularity=s["popularity"], ratings_repo=s["repo"])


def get_similar_uc() -> GetSimilarUseCase:
    s = _services()
    return GetSimilarUseCase(content=s["content"], ratings_repo=s["repo"])


def get_search_uc() -> SearchByQueryUseCase:
    s = _services()
    return SearchByQueryUseCase(content=s["content"])


def get_recommendations_uc() -> GetRecommendationsUseCase:
    s = _services()
    return GetRecommendationsUseCase(
        ratings_repo=s["repo"],
        popularity=s["popularity"],
        content=s["content"],
        hybrid=s["hybrid"],
    )


def get_save_rating_uc() -> SaveRatingUseCase:
    s = _services()
    return SaveRatingUseCase(ratings_repo=s["repo"])


def get_book_metrics_uc() -> GetBookMetricsUseCase:
    s = _services()
    return GetBookMetricsUseCase(ratings_repo=s["repo"])
