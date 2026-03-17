from core.domain.model.book import BookRecommendation
from core.ports.recommendation_service import IContentService

GENRE_KEYWORDS: dict[str, list[str]] = {
    "fantasy": ["магия", "дракон", "fantasy", "magic", "wizard"],
    "mystery": ["детектив", "убийство", "mystery", "detective", "crime"],
    "romance": ["любовь", "romance", "love", "relationship"],
    "science-fiction": ["космос", "робот", "sci-fi", "space", "future"],
    "horror": ["ужас", "страх", "horror", "scary", "ghost"],
    "thriller": ["триллер", "thriller", "suspense", "conspiracy"],
}


def _detect_genre(text: str) -> str | None:
    lower = text.lower()
    for genre, keywords in GENRE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return genre
    return None


class SearchByQueryUseCase:
    def __init__(self, content: IContentService) -> None:
        self._content = content

    def execute(self, query: str, n: int = 10) -> list[BookRecommendation]:
        genre_filter = _detect_genre(query)
        return self._content.get_similar_by_query(
            query=query, n=n, genre_filter=genre_filter
        )
