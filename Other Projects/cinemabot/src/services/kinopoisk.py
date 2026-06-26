"""Kinopoisk Unofficial API client."""

import logging
from dataclasses import dataclass, field
from typing import Optional

from src.services.http_client import http_client

logger = logging.getLogger(__name__)

# API endpoints
BASE_URL = "https://kinopoiskapiunofficial.tech/api"
SEARCH_URL = f"{BASE_URL}/v2.1/films/search-by-keyword"
DETAILS_URL = f"{BASE_URL}/v2.2/films"
STAFF_URL = f"{BASE_URL}/v1/staff"


@dataclass
class Movie:
    """Movie data structure."""

    id: int
    title: str
    original_title: Optional[str] = None
    year: Optional[str] = None
    rating: Optional[str] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    duration: Optional[str] = None
    genres: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    directors: list[str] = field(default_factory=list)
    actors: list[str] = field(default_factory=list)


class KinopoiskService:
    """Service for interacting with Kinopoisk API."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

    async def search(self, query: str) -> list[Movie]:
        """
        Search movies by keyword.

        Args:
            query: Search query string

        Returns:
            List of Movie objects
        """
        data = await http_client.get_json(
            SEARCH_URL,
            headers=self._headers,
            params={"keyword": query, "page": 1},
        )

        if not data or not data.get("films"):
            return []

        return [self._parse_movie(film) for film in data["films"]]

    async def get_details(self, movie_id: int) -> Optional[Movie]:
        """
        Get detailed movie information.

        Args:
            movie_id: Kinopoisk movie ID

        Returns:
            Movie object or None if not found
        """
        data = await http_client.get_json(
            f"{DETAILS_URL}/{movie_id}",
            headers=self._headers,
        )

        if not data:
            return None

        return self._parse_movie(data)

    async def get_staff(self, movie_id: int) -> tuple[list[str], list[str]]:
        """
        Get movie staff (directors and actors).

        Args:
            movie_id: Kinopoisk movie ID

        Returns:
            Tuple of (directors list, actors list)
        """
        data = await http_client.get_json(
            STAFF_URL,
            headers=self._headers,
            params={"filmId": movie_id},
        )

        if not data:
            return [], []

        directors = []
        actors = []

        if not isinstance(data, list):
            return [], []

        for person in data:
            if not isinstance(person, dict):
                continue
            name = person.get("nameRu") or person.get("nameEn") or ""

            if not name:
                continue

            profession = person.get("professionKey")
            if profession == "DIRECTOR":
                directors.append(name)
            elif profession == "ACTOR" and len(actors) < 5:
                actors.append(name)

        return directors, actors

    async def search_with_details(self, query: str) -> list[Movie]:
        """
        Search movies and enrich first result with staff info.

        Args:
            query: Search query string

        Returns:
            List of Movie objects (first one with full details)
        """
        movies = await self.search(query)

        if movies and movies[0].id:
            directors, actors = await self.get_staff(movies[0].id)
            movies[0].directors = directors
            movies[0].actors = actors

        return movies

    def _parse_movie(self, data: dict) -> Movie:
        """Parse API response into Movie object."""
        movie_id = data.get("filmId") or data.get("kinopoiskId") or 0

        return Movie(
            id=movie_id,
            title=data.get("nameRu") or data.get("nameEn") or "Unknown",
            original_title=data.get("nameEn"),
            year=str(data.get("year", "")) or None,
            rating=str(data.get("rating", "")) or None,
            description=data.get("description"),
            poster_url=data.get("posterUrl") or data.get("posterUrlPreview"),
            duration=str(data.get("filmLength", "")) or None,
            genres=[g.get("genre", "") for g in data.get("genres", []) if g.get("genre")],
            countries=[c.get("country", "") for c in data.get("countries", []) if c.get("country")],
        )
