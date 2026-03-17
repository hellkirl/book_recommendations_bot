from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

GENRE_EMOJI: dict[str, str] = {
    "fantasy": "🧙",
    "science-fiction": "🚀",
    "mystery": "🔍",
    "romance": "💕",
    "horror": "👻",
    "thriller": "😱",
    "poetry": "📜",
    "fiction": "📖",
    "non-fiction": "📚",
    "biography": "👤",
    "history": "🏛️",
    "philosophy": "🤔",
    "psychology": "🧠",
    "science": "🔬",
    "children": "👶",
    "young-adult": "🎓",
    "classics": "🎭",
    "drama": "🎪",
    "adventure": "🗺️",
    "humor": "😂",
}

GENRE_RU: dict[str, str] = {
    "fantasy": "Фэнтези",
    "science-fiction": "Научная фантастика",
    "mystery": "Детектив",
    "romance": "Романтика",
    "horror": "Ужасы",
    "thriller": "Триллер",
    "poetry": "Поэзия",
    "fiction": "Художественная",
    "non-fiction": "Нон-фикшн",
    "biography": "Биография",
    "history": "История",
    "philosophy": "Философия",
    "psychology": "Психология",
    "science": "Наука",
    "children": "Детские",
    "young-adult": "Подростковые",
    "classics": "Классика",
    "drama": "Драма",
    "adventure": "Приключения",
    "humor": "Юмор",
}


def _genre_label(genre: str) -> str:
    emoji = GENRE_EMOJI.get(genre.lower(), "📚")
    ru_name = GENRE_RU.get(genre.lower(), genre.capitalize())
    return f"{emoji} {ru_name}"


def genres_keyboard(genres: list[str]) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for genre in genres:
        btn = InlineKeyboardButton(
            text=_genre_label(genre), callback_data=f"genre:{genre}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def rating_keyboard(book_id: int) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=f"{i}{'⭐' * i}", callback_data=f"rate:{book_id}:{i}")
        for i in range(1, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📚 Жанры", callback_data="menu:genres"),
            InlineKeyboardButton(text="🔥 В тренде", callback_data="menu:trending"),
        ],
        [
            InlineKeyboardButton(
                text="✨ Рекомендации", callback_data="menu:recommend"
            ),
            InlineKeyboardButton(text="🔍 Поиск", callback_data="menu:search"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu:help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
