"""Cinema Bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import load_config
from src.database.repository import Repository
from src.services.kinopoisk import KinopoiskService
from src.services.http_client import http_client
from src.handlers import routers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and start the bot."""
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded")

    # Initialize services
    repository = Repository(config.database_path)
    await repository.init()

    kinopoisk_service = KinopoiskService(config.kinopoisk_api_key)
    await http_client.start()

    # Initialize bot
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register routers
    for router in routers:
        dp.include_router(router)

    logger.info("Starting bot...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # Pass dependencies through dispatcher workflow_data
        await dp.start_polling(
            bot,
            kinopoisk=kinopoisk_service,
            repository=repository,
        )
    finally:
        await http_client.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
