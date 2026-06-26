"""Movie search handlers."""

import logging
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.services.kinopoisk import KinopoiskService, Movie
from src.database.repository import Repository
from src.utils.formatters import format_movie_card
from src.utils.keyboards import build_watch_keyboard, build_more_results_keyboard

logger = logging.getLogger(__name__)

router = Router()

VIEW_PATTERN = re.compile(r"^/view_(\d+)$")


async def send_movie_card(
    message: Message,
    movie: Movie,
    repository: Repository,
    other_movies: list[Movie] | None = None,
) -> None:
    """
    Send formatted movie card with poster and watch links.

    Args:
        message: Telegram message to reply to
        movie: Main movie to display
        repository: Database repository for saving history
        other_movies: Optional list of alternative results
    """
    text = format_movie_card(movie)
    keyboard = build_watch_keyboard(movie.title)

    # Save to history
    if movie.id:
        await repository.save_search(
            user_id=message.from_user.id,
            movie_id=movie.id,
            title=movie.title,
        )

    # Send main card with poster
    try:
        if movie.poster_url:
            await message.answer_photo(
                photo=movie.poster_url,
                caption=text,
                reply_markup=keyboard,
            )
        else:
            await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning(f"Failed to send photo: {e}")
        await message.answer(text[:4096], reply_markup=keyboard)

    # Send alternative results as separate message with buttons
    if other_movies:
        more_keyboard = build_more_results_keyboard(other_movies)
        if more_keyboard:
            await message.answer(
                "🔍 <b>Также найдено:</b>",
                reply_markup=more_keyboard,
            )


@router.callback_query(F.data.startswith("movie:"))
async def callback_view_movie(
    callback: CallbackQuery,
    kinopoisk: KinopoiskService,
    repository: Repository,
) -> None:
    """Handle movie selection from inline keyboard."""
    # Extract movie ID from callback data
    movie_id = int(callback.data.split(":")[1])

    # Acknowledge the callback to remove "loading" state
    await callback.answer()

    # Show typing indicator
    await callback.message.bot.send_chat_action(callback.message.chat.id, "typing")

    # Get movie details
    movie = await kinopoisk.get_details(movie_id)
    if not movie:
        await callback.message.answer("❌ Фильм не найден.")
        return

    # Load staff info
    directors, actors = await kinopoisk.get_staff(movie_id)
    movie.directors = directors
    movie.actors = actors

    # Send card
    # Note: callback.message.from_user is the bot, so we need callback.from_user
    # But save_search uses message.from_user.id, so we create a wrapper
    await send_movie_card_for_callback(callback, movie, repository)


async def send_movie_card_for_callback(
    callback: CallbackQuery,
    movie: Movie,
    repository: Repository,
) -> None:
    """
    Send movie card in response to callback query.

    Similar to send_movie_card but handles user_id correctly for callbacks.
    """
    text = format_movie_card(movie)
    keyboard = build_watch_keyboard(movie.title)

    # Save to history (use callback.from_user for correct user_id)
    if movie.id:
        await repository.save_search(
            user_id=callback.from_user.id,
            movie_id=movie.id,
            title=movie.title,
        )

    # Send card
    try:
        if movie.poster_url:
            await callback.message.answer_photo(
                photo=movie.poster_url,
                caption=text,
                reply_markup=keyboard,
            )
        else:
            await callback.message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning(f"Failed to send photo: {e}")
        await callback.message.answer(text[:4096], reply_markup=keyboard)


@router.message(F.text.regexp(VIEW_PATTERN))
async def view_by_id(
    message: Message,
    kinopoisk: KinopoiskService,
    repository: Repository,
) -> None:
    """Handle /view_ID commands to show specific movie."""
    match = VIEW_PATTERN.match(message.text)
    if not match:
        return

    movie_id = int(match.group(1))

    await message.bot.send_chat_action(message.chat.id, "typing")

    movie = await kinopoisk.get_details(movie_id)
    if not movie:
        await message.answer("❌ Фильм не найден.")
        return

    # Load staff info
    directors, actors = await kinopoisk.get_staff(movie_id)
    movie.directors = directors
    movie.actors = actors

    await send_movie_card(message, movie, repository)


@router.message(F.text & ~F.text.startswith("/"))
async def search_movie(
    message: Message,
    kinopoisk: KinopoiskService,
    repository: Repository,
) -> None:
    """Handle free text search queries."""
    query = message.text.strip()
    if not query:
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    movies = await kinopoisk.search_with_details(query)

    if not movies:
        await message.answer(
            "😔 Ничего не найдено.\n"
            "Попробуй изменить запрос или проверь написание."
        )
        return

    # First movie is main, rest are alternatives
    main_movie = movies[0]
    other_movies = movies[1:6]  # Up to 5 alternatives

    await send_movie_card(message, main_movie, repository, other_movies)
