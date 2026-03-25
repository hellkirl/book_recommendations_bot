from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from adapters.inbound.http.api.dependencies import (
    get_popular_uc,
    get_similar_uc,
    get_search_uc,
    get_recommendations_uc,
    get_save_rating_uc,
    get_record_book_interaction_uc,
)
from adapters.outbound.ml.model_loader import get_artifacts
from .keyboards import genres_keyboard, rating_keyboard, main_menu_keyboard, GENRE_RU

router = Router()


GENRE_ALIASES_RU: dict[str, str] = {
    "classic": "Классика",
    "poem": "Поэзия",
    "poems": "Поэзия",
    "plays": "Пьесы",
    "play": "Пьесы",
    "nonfiction": "Нон-фикшн",
    "essay": "Эссе",
    "essays": "Эссе",
    "reference": "Справочник",
    "textbooks": "Учебники",
    "textbook": "Учебник",
    "feminism": "Феминизм",
    "queer": "Квир",
    "humour": "Юмор",
    "bangla": "Бенгальская литература",
    "bengali": "Бенгальская литература",
    "persian": "Персидская литература",
    "persian-literature": "Персидская литература",
    "iranian": "Иранская литература",
    "iran": "Иранская литература",
    "art": "Искусство",
}


class SearchState(StatesGroup):
    waiting_for_query = State()


def _format_genre(genre: str | None) -> str | None:
    if not genre:
        return None

    raw_tags = [tag.strip().lower() for tag in genre.split() if tag.strip()]
    if not raw_tags:
        return None

    translated: list[str] = []
    seen: set[str] = set()
    for tag in raw_tags:
        label = GENRE_RU.get(tag) or GENRE_ALIASES_RU.get(tag)
        if not label:
            continue
        if label in seen:
            continue
        translated.append(label)
        seen.add(label)
        if len(translated) == 3:
            break

    if translated:
        return ", ".join(translated)

    fallback = raw_tags[0].replace("-", " ").replace("_", " ")
    return fallback.capitalize()


def _format_books(books: list) -> str:
    if not books:
        return "😔 Ничего не найдено."

    lines: list[str] = []
    for i, b in enumerate(books, 1):
        parts = [f"<b>{i}. {b.title}</b>"]
        if b.genre:
            genre_label = _format_genre(b.genre)
            if genre_label:
                parts.append(f"    📂 {genre_label}")
        parts.append(f"    🔗 /similar_{b.book_id}  ·  ⭐ /rate_{b.book_id}")

        lines.append("\n".join(parts))

    return "\n\n".join(lines)


def _get_book_title(book_id: int) -> str:
    try:
        arts = get_artifacts()
        cb_idx = arts.book_id_to_cb_idx.get(book_id)
        if cb_idx is not None:
            return str(arts.cb_meta.iloc[cb_idx]["title"])
    except Exception:
        pass
    return f"#{book_id}"


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "📚 <b>Книговод</b> — ваш персональный помощник в мире книг!\n\n"
        "Я помогу вам найти интересные книги на основе ваших предпочтений.\n\n"
        "🎯 <b>Что я умею:</b>\n"
        "├ 📚 Подбирать книги по жанрам\n"
        "├ 🔥 Показывать трендовые книги\n"
        "├ 🔍 Искать по описанию\n"
        "├ 📖 Находить похожие книги\n"
        "└ ✨ Давать персональные рекомендации\n\n"
        "💡 <i>Оцените 10+ книг, чтобы получить персональные рекомендации!</i>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Справка по командам</b>\n\n"
        "🔹 /genres — выбрать жанр\n"
        "🔹 /trending — книги в тренде\n"
        "🔹 /search <i>запрос</i> — поиск по описанию\n"
        "🔹 /similar <i>id</i> — похожие книги\n"
        "🔹 /recommend — персональные рекомендации\n"
        "🔹 /rate <i>id</i> <i>1-5</i> — оценить книгу\n\n"
        "💡 <b>Совет:</b> Оцените минимум 10 книг для персональных рекомендаций!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "📋 <b>Главное меню</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu:genres")
async def cb_menu_genres(callback: CallbackQuery):
    arts = get_artifacts()
    await callback.message.answer(
        "📚 <b>Выберите жанр</b>\n\nНажмите на интересующий вас жанр:",
        parse_mode="HTML",
        reply_markup=genres_keyboard(arts.top_genres),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:trending")
async def cb_menu_trending(callback: CallbackQuery):
    uc = get_popular_uc()
    books = uc.execute(mode="trends", telegram_id=callback.from_user.id, n=10)
    record_uc = get_record_book_interaction_uc()
    for b in books:
        record_uc.execute_impression(book_id=b.book_id, telegram_id=callback.from_user.id)
    await callback.message.answer(
        f"🔥 <b>Сейчас в тренде</b>\n\n{_format_books(books)}",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "menu:recommend")
async def cb_menu_recommend(callback: CallbackQuery):
    uc = get_recommendations_uc()
    books = uc.execute(telegram_id=callback.from_user.id, n=10)

    if not books:
        text = (
            "😕 <b>Пока нет рекомендаций</b>\n\n"
            "Оцените несколько книг, чтобы я мог понять ваши предпочтения!\n\n"
            "💡 Начните с просмотра жанров или трендов."
        )
    else:
        record_uc = get_record_book_interaction_uc()
        for b in books:
            record_uc.execute_impression(book_id=b.book_id, telegram_id=callback.from_user.id)
        text = f"✨ <b>Рекомендации для вас</b>\n\n{_format_books(books)}"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "menu:search")
async def cb_menu_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchState.waiting_for_query)
    await callback.message.answer(
        "🔍 <b>Поиск книг</b>\n\n"
        "Опишите, какую книгу вы ищете.\n\n"
        "💡 <i>Примеры запросов:</i>\n"
        "• детектив в викторианской Англии\n"
        "• книга про космические путешествия\n"
        "• романтическая история о любви",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def cb_menu_help(callback: CallbackQuery):
    await callback.message.answer(
        "📖 <b>Справка по командам</b>\n\n"
        "🔹 /genres — выбрать жанр\n"
        "🔹 /trending — книги в тренде\n"
        "🔹 /search <i>запрос</i> — поиск по описанию\n"
        "🔹 /similar <i>id</i> — похожие книги\n"
        "🔹 /recommend — персональные рекомендации\n"
        "🔹 /rate <i>id</i> <i>1-5</i> — оценить книгу\n\n"
        "💡 <b>Совет:</b> Оцените минимум 10 книг для персональных рекомендаций!",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("genres"))
async def cmd_genres(message: Message):
    arts = get_artifacts()
    await message.answer(
        "📚 <b>Выберите жанр</b>\n\nНажмите на интересующий вас жанр:",
        parse_mode="HTML",
        reply_markup=genres_keyboard(arts.top_genres),
    )


@router.callback_query(F.data.startswith("genre:"))
async def cb_genre(callback: CallbackQuery):
    genre = callback.data.split(":", 1)[1]
    genre_ru = GENRE_RU.get(genre.lower(), genre.capitalize())

    uc = get_popular_uc()
    books = uc.execute(
        mode="genre",
        genre=genre,
        telegram_id=callback.from_user.id,
        n=10,
    )
    record_uc = get_record_book_interaction_uc()
    for b in books:
        record_uc.execute_impression(book_id=b.book_id, telegram_id=callback.from_user.id)
    await callback.message.answer(
        f"📖 <b>Лучшее в жанре «{genre_ru}»</b>\n\n{_format_books(books)}",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("trending"))
async def cmd_trending(message: Message):
    uc = get_popular_uc()
    books = uc.execute(mode="trends", telegram_id=message.from_user.id, n=10)
    record_uc = get_record_book_interaction_uc()
    for b in books:
        record_uc.execute_impression(book_id=b.book_id, telegram_id=message.from_user.id)
    await message.answer(
        f"🔥 <b>Сейчас в тренде</b>\n\n{_format_books(books)}",
        parse_mode="HTML",
    )


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    query = message.text.partition(" ")[2].strip()
    if not query:
        await state.set_state(SearchState.waiting_for_query)
        await message.answer(
            "🔍 <b>Поиск книг</b>\n\n"
            "Опишите, какую книгу вы ищете.\n\n"
            "💡 <i>Примеры запросов:</i>\n"
            "• детектив в викторианской Англии\n"
            "• книга про космические путешествия\n"
            "• романтическая история о любви",
            parse_mode="HTML",
        )
        return
    await _do_search(message, query)


@router.message(SearchState.waiting_for_query)
async def handle_search_query(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
    if not query:
        await message.answer("❌ Пустой запрос. Попробуйте ещё раз.")
        return
    await _do_search(message, query)


async def _do_search(message: Message, query: str):
    uc = get_search_uc()
    books = uc.execute(query=query, n=10)
    record_uc = get_record_book_interaction_uc()
    for b in books:
        record_uc.execute_impression(book_id=b.book_id, telegram_id=message.from_user.id)
    await message.answer(
        f"🔍 <b>Результаты поиска: «{query}»</b>\n\n{_format_books(books)}",
        parse_mode="HTML",
    )


@router.message(Command("similar"))
async def cmd_similar(message: Message):
    arg = message.text.partition(" ")[2].strip()
    if not arg:
        await message.answer(
            "📖 <b>Поиск похожих книг</b>\n\n"
            "Использование: /similar <i>id_книги</i>\n\n"
            "💡 ID книги можно найти в результатах поиска или рекомендациях.",
            parse_mode="HTML",
        )
        return
    try:
        book_id = int(arg)
    except ValueError:
        await message.answer("❌ ID книги должен быть числом.")
        return
    await _do_similar(message, book_id)


@router.message(F.text.regexp(r"^/similar_(\d+)"))
async def cmd_similar_shortcut(message: Message):
    book_id = int(message.text.split("_", 1)[1])
    record_uc = get_record_book_interaction_uc()
    record_uc.execute_click(book_id=book_id, telegram_id=message.from_user.id)
    await _do_similar(message, book_id)


async def _do_similar(message: Message, book_id: int):
    book_title = _get_book_title(book_id)
    uc = get_similar_uc()
    books = uc.execute(book_id=book_id, telegram_id=message.from_user.id, n=10)
    record_uc = get_record_book_interaction_uc()
    for b in books:
        record_uc.execute_impression(book_id=b.book_id, telegram_id=message.from_user.id)
    await message.answer(
        f"📖 <b>Похожие на «{book_title}»</b>\n\n{_format_books(books)}",
        parse_mode="HTML",
    )


@router.message(Command("recommend"))
async def cmd_recommend(message: Message):
    uc = get_recommendations_uc()
    books = uc.execute(telegram_id=message.from_user.id, n=10)

    if not books:
        text = (
            "😕 <b>Пока нет рекомендаций</b>\n\n"
            "Оцените несколько книг, чтобы я мог понять ваши предпочтения!\n\n"
            "💡 Начните с просмотра жанров (/genres) или трендов (/trending)."
        )
    else:
        record_uc = get_record_book_interaction_uc()
        for b in books:
            record_uc.execute_impression(book_id=b.book_id, telegram_id=message.from_user.id)
        text = f"✨ <b>Рекомендации для вас</b>\n\n{_format_books(books)}"

    await message.answer(text, parse_mode="HTML")


@router.message(Command("rate"))
async def cmd_rate(message: Message):
    parts = message.text.split()
    if len(parts) == 3:
        try:
            book_id, score = int(parts[1]), int(parts[2])
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат</b>\n\n"
                "Использование: /rate <i>id_книги</i> <i>оценка</i>\n"
                "Оценка от 1 до 5.",
                parse_mode="HTML",
            )
            return
        record_uc = get_record_book_interaction_uc()
        record_uc.execute_click(book_id=book_id, telegram_id=message.from_user.id)
        await _do_rate(message, book_id, score)
    elif len(parts) == 2:
        try:
            book_id = int(parts[1])
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат</b>\n\n"
                "Использование: /rate <i>id_книги</i> <i>оценка</i>",
                parse_mode="HTML",
            )
            return
        record_uc = get_record_book_interaction_uc()
        record_uc.execute_click(book_id=book_id, telegram_id=message.from_user.id)
        book_title = _get_book_title(book_id)
        await message.answer(
            f"⭐ <b>Оцените книгу</b>\n\n«{book_title}»\n\nВыберите оценку:",
            parse_mode="HTML",
            reply_markup=rating_keyboard(book_id),
        )
    else:
        await message.answer(
            "⭐ <b>Оценка книги</b>\n\n"
            "Использование: /rate <i>id_книги</i> <i>оценка</i>\n\n"
            "💡 Или нажмите на кнопку оценки рядом с книгой.",
            parse_mode="HTML",
        )


@router.message(F.text.regexp(r"^/rate_(\d+)$"))
async def cmd_rate_shortcut(message: Message):
    book_id = int(message.text.split("_", 1)[1])
    record_uc = get_record_book_interaction_uc()
    record_uc.execute_click(book_id=book_id, telegram_id=message.from_user.id)
    book_title = _get_book_title(book_id)
    await message.answer(
        f"⭐ <b>Оцените книгу</b>\n\n«{book_title}»\n\nВыберите оценку:",
        parse_mode="HTML",
        reply_markup=rating_keyboard(book_id),
    )


@router.callback_query(F.data.startswith("rate:"))
async def cb_rate(callback: CallbackQuery):
    _, book_id_str, score_str = callback.data.split(":")
    book_id, score = int(book_id_str), int(score_str)
    record_uc = get_record_book_interaction_uc()
    record_uc.execute_click(book_id=book_id, telegram_id=callback.from_user.id)
    await _do_rate(callback.message, book_id, score, user_id=callback.from_user.id)
    await callback.answer("Оценка сохранена! ✨")


async def _do_rate(
    message: Message, book_id: int, score: int, user_id: int | None = None
):
    uid = user_id or message.from_user.id
    if not 1 <= score <= 5:
        await message.answer("❌ Оценка должна быть от 1 до 5.")
        return

    uc = get_save_rating_uc()
    unlocked = uc.execute(telegram_id=uid, book_id=book_id, score=score)

    book_title = _get_book_title(book_id)
    stars = "⭐" * score + "☆" * (5 - score)

    text = f"✅ <b>Оценка сохранена!</b>\n\n«{book_title}»\n{stars}"

    if unlocked:
        text += (
            "\n\n🎉 <b>Поздравляем!</b>\n"
            "Вы оценили 10+ книг — персональные рекомендации разблокированы!\n\n"
            "Попробуйте /recommend"
        )

    await message.answer(text, parse_mode="HTML")
