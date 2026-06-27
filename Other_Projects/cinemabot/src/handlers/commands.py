"""Basic bot commands: /start, /help."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "👋 <b>Привет!</b> Я бот для поиска фильмов и сериалов.\n\n"
        "Просто напиши название, и я найду информацию о нём "
        "и покажу где посмотреть.\n\n"
        "Используй /help для подробностей."
    )

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "🎥 <b>Как пользоваться ботом:</b>\n\n"
        "Просто отправь название фильма или сериала текстом.\n"
        "Я найду информацию, рейтинг, и дам ссылки для просмотра.\n\n"
        "<b>Примеры запросов:</b>\n"
        "Venom\n"
        "остров собак\n"
        "магия лунного света\n"
        "Мстители: война бесконечности\n"
        "город в котором меня нет\n"
        "как витька чеснок вез леху штыря в дом инвалидов\n\n"
        "<b>Команды:</b>\n"
        "/history — история твоих поисков\n"
        "/stats — статистика просмотров"
    )
