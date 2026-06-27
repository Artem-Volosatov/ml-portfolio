"""Database operations for search history and statistics."""

import aiosqlite
import logging
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)


class HistoryRecord(NamedTuple):
    """Single history record."""
    movie_id: int
    title: str
    created_at: str


class StatsRecord(NamedTuple):
    """Movie statistics record."""
    movie_id: int
    title: str
    search_count: int


class Repository:
    """Database repository for user data."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def init(self) -> None:
        """Initialize database schema."""
        # Ensure directory exists
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_user
                ON history(user_id)
            """)
            await db.commit()

        logger.info(f"Database initialized at {self._db_path}")

    async def save_search(
        self,
        user_id: int,
        movie_id: int,
        title: str,
    ) -> None:
        """
        Save search record to history.

        Args:
            user_id: Telegram user ID
            movie_id: Kinopoisk movie ID
            title: Movie title
        """
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO history (user_id, movie_id, title) VALUES (?, ?, ?)",
                (user_id, movie_id, title),
            )
            await db.commit()

    async def get_history(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[HistoryRecord]:
        """
        Get user's search history.

        Args:
            user_id: Telegram user ID
            limit: Maximum records to return

        Returns:
            List of HistoryRecord objects
        """
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT movie_id, title, created_at
                FROM history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    HistoryRecord(movie_id=row[0], title=row[1], created_at=row[2])
                    for row in rows
                ]

    async def get_stats(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[StatsRecord]:
        """
        Get user's movie statistics.

        Args:
            user_id: Telegram user ID
            limit: Maximum records to return

        Returns:
            List of StatsRecord objects (movie_id, title, search_count)
        """
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT movie_id, title, COUNT(*) as count
                FROM history
                WHERE user_id = ?
                GROUP BY movie_id
                ORDER BY count DESC
                LIMIT ?
                """,
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    StatsRecord(movie_id=row[0], title=row[1], search_count=row[2])
                    for row in rows
                ]
