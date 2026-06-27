"""Application configuration from environment variables."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Bot configuration."""

    bot_token: str
    kinopoisk_api_key: str
    database_path: str = "data/cinema_bot.db"

    # Limits
    max_search_results: int = 5
    max_description_length: int = 500
    max_history_items: int = 10
    max_stats_items: int = 10


def load_config() -> Config:
    """Load configuration from environment variables."""
    bot_token = os.getenv("BOT_TOKEN")
    kino_token = os.getenv("KINO_TOKEN")

    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")
    if not kino_token:
        raise ValueError("KINO_TOKEN environment variable is required")

    return Config(
        bot_token=bot_token,
        kinopoisk_api_key=kino_token,
        database_path=os.getenv("DATABASE_PATH", "data/cinema_bot.db"),
    )
