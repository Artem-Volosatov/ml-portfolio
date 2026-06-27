"""Tests for Kinopoisk service."""

import pytest
from src.services.kinopoisk import KinopoiskService, Movie


class TestMovieDataclass:
    """Tests for Movie dataclass."""

    def test_default_values(self):
        movie = Movie(id=1, title="Test")
        assert movie.id == 1
        assert movie.title == "Test"
        assert movie.genres == []
        assert movie.countries == []
        assert movie.directors == []
        assert movie.actors == []

    def test_all_fields(self):
        movie = Movie(
            id=123,
            title="Тест",
            original_title="Test",
            year="2024",
            rating="8.0",
            description="Description",
            poster_url="http://example.com/poster.jpg",
            duration="120",
            genres=["драма", "комедия"],
            countries=["Россия"],
        )
        assert movie.id == 123
        assert movie.genres == ["драма", "комедия"]


class TestKinopoiskService:
    """Tests for KinopoiskService."""

    def test_parse_movie_minimal(self):
        service = KinopoiskService("fake_key")
        data = {"kinopoiskId": 123, "nameRu": "Тест"}
        movie = service._parse_movie(data)

        assert movie.id == 123
        assert movie.title == "Тест"

    def test_parse_movie_with_filmId(self):
        service = KinopoiskService("fake_key")
        data = {"filmId": 456, "nameRu": "Фильм"}
        movie = service._parse_movie(data)

        assert movie.id == 456

    def test_parse_movie_fallback_to_english_title(self):
        service = KinopoiskService("fake_key")
        data = {"kinopoiskId": 1, "nameEn": "English Title"}
        movie = service._parse_movie(data)

        assert movie.title == "English Title"

    def test_parse_movie_genres(self):
        service = KinopoiskService("fake_key")
        data = {
            "kinopoiskId": 1,
            "nameRu": "Test",
            "genres": [{"genre": "драма"}, {"genre": "комедия"}],
        }
        movie = service._parse_movie(data)

        assert movie.genres == ["драма", "комедия"]
