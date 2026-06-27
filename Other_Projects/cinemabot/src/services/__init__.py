"""Services package - external API clients and business logic."""

from src.services.http_client import http_client, HttpClient
from src.services.kinopoisk import KinopoiskService, Movie

__all__ = [
    "http_client",
    "HttpClient",
    "KinopoiskService",
    "Movie",
]
