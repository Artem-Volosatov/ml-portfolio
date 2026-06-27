"""User statistics handlers: /history, /stats."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.repository import Repository

router = Router()


@router.message(Command("history"))
async def cmd_history(message: Message, repository: Repository) -> None:
    """Handle /history command - show user's search history."""
    user_id = message.from_user.id
    records = await repository.get_history(user_id, limit=10)

    if not records:
        await message.answer("📜 История поиска пуста.")
        return

    lines = ["📜 <b>Последние поиски:</b>\n"]
    for record in records:
        lines.append(f"• {record.title} /view_{record.movie_id}")

    await message.answer("\n".join(lines))


@router.message(Command("stats"))
async def cmd_stats(message: Message, repository: Repository) -> None:
    """Handle /stats command - show user's movie statistics."""
    user_id = message.from_user.id
    records = await repository.get_stats(user_id, limit=10)

    if not records:
        await message.answer("📊 Статистика пуста.")
        return

    lines = ["📊 <b>Топ твоих фильмов:</b>\n"]
    for record in records:
        lines.append(
            f"• {record.title} ({record.search_count}×) /view_{record.movie_id}"
        )

    await message.answer("\n".join(lines))
