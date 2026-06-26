"""Inline keyboard builders."""

from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.kinopoisk import Movie


def build_watch_keyboard(movie_title: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard with search links for watching movie.

    Args:
        movie_title: Movie title for search queries

    Returns:
        InlineKeyboardMarkup with video platform links
    """
    # Clean query for video platforms
    query = quote(movie_title)

    # Extended query for search engines (exclude trailers)
    search_query = quote(f"{movie_title} смотреть онлайн -трейлер")

    buttons = [
        [
            InlineKeyboardButton(
                text="📺 VK Video",
                url=f"https://vkvideo.ru/?content_type=video&duration=long&q={query}",
            ),
            InlineKeyboardButton(
                text="🎬 Rutube",
                url=f"https://rutube.ru/search/?content_type=video&query={query}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🌀 Dzen",
                url=f"https://dzen.ru/search?query={query}&type_filter=video",
            ),
            InlineKeyboardButton(
                text="▶️ YouTube",
                url=f"https://www.youtube.com/results?search_query={search_query}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔍 Яндекс",
                url=f"https://yandex.ru/video/search?text={search_query}",
            ),
            InlineKeyboardButton(
                text="🔎 Google",
                url=f"https://www.google.com/search?q={search_query}&tbm=vid",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def build_more_results_keyboard(movies: list["Movie"]) -> InlineKeyboardMarkup | None:
    """
    Build keyboard with alternative movie results.

    Args:
        movies: List of alternative movies

    Returns:
        InlineKeyboardMarkup or None if no movies
    """
    if not movies:
        return None

    buttons = []
    for movie in movies[:5]:
        if not movie.id:
            continue

        text = movie.title
        if movie.year:
            text += f" ({movie.year})"

        if len(text) > 60:
            text = text[:57] + "..."

        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"movie:{movie.id}"
            )
        ])

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=buttons)
