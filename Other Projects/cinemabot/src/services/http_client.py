"""Reusable async HTTP client."""

import aiohttp
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HttpClient:
    """Async HTTP client with session reuse."""

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        """Initialize the HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Optional[dict[str, Any]]:
        """
        Perform GET request and return JSON response.

        Args:
            url: Request URL
            headers: Optional HTTP headers
            params: Optional query parameters

        Returns:
            Parsed JSON response or None on error
        """
        if self._session is None or self._session.closed:
            await self.start()

        session = self._session
        assert session is not None  # For type checker

        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"HTTP {response.status} for {url}")
                return None
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            return None


# Global instance for reuse
http_client = HttpClient()
