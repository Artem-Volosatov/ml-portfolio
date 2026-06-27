"""Tests for formatting utilities."""

import pytest
from src.services.kinopoisk import Movie
from src.utils.formatters import format_duration, format_movie_card


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_none_returns_empty(self):
        assert format_duration(None) == ""

    def test_empty_string_returns_empty(self):
        assert format_duration("") == ""

    def test_minutes_only(self):
        assert format_duration(45) == "45мин"
        assert format_duration("45") == "45мин"

    def test_hours_and_minutes(self):
        assert format_duration(90) == "1ч 30мин"
        assert format_duration(120) == "2ч 0мин"
        assert format_duration("150") == "2ч 30мин"

    def test_invalid_returns_as_string(self):
        assert format_duration("invalid") == "invalid"


class TestFormatMovieCard:
    """Tests for format_movie_card function."""

    def test_minimal_movie(self):
        movie = Movie(id=1, title="Test Movie")
        result = format_movie_card(movie)
        assert "<b>Test Movie</b>" in result

    def test_movie_with_year(self):
        movie = Movie(id=1, title="Test Movie", year="2024")
        result = format_movie_card(movie)
        assert "<b>Test Movie</b> (2024)" in result

    def test_movie_with_rating(self):
        movie = Movie(id=1, title="Test", rating="8.5")
        result = format_movie_card(movie)
        assert "⭐ Рейтинг: 8.5" in result

    def test_rating_none_not_shown(self):
        movie = Movie(id=1, title="Test", rating="None")
        result = format_movie_card(movie)
        assert "Рейтинг" not in result

    def test_movie_with_staff(self):
        movie = Movie(
            id=1,
            title="Test",
            directors=["Director One"],
            actors=["Actor One", "Actor Two"],
        )
        result = format_movie_card(movie)
        assert "🎬 Режиссёр: Director One" in result
        assert "🎭 В ролях: Actor One, Actor Two" in result

    def test_long_description_truncated(self):
        long_desc = "A" * 600
        movie = Movie(id=1, title="Test", description=long_desc)
        result = format_movie_card(movie)
        assert len(result) < len(long_desc)
        assert result.endswith("...")
