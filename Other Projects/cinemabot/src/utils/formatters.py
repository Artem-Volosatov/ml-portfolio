"""Message formatting utilities."""

from src.services.kinopoisk import Movie

MAX_DESCRIPTION_LENGTH = 500


def format_duration(duration: str | int | None) -> str:
    """
    Format duration to human-readable string.

    Handles multiple formats:
    - "2:17" (hours:minutes from API) -> "2ч 17мин"
    - "137" (minutes as string) -> "2ч 17мин"
    - 137 (minutes as int) -> "2ч 17мин"
    - None or empty -> ""

    Args:
        duration: Duration in various formats

    Returns:
        Formatted string like "2ч 17мин" or empty string
    """
    if not duration:
        return ""

    s = str(duration).strip()
    if not s:
        return ""

    # Format 1: "H:MM" or "HH:MM" (hours:minutes from API)
    if ":" in s:
        try:
            parts = s.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])

            if hours > 0:
                return f"{hours}ч {minutes}мин"
            elif minutes > 0:
                return f"{minutes}мин"
            return ""
        except (ValueError, IndexError):
            return s  # Return as-is if parsing fails

    # Format 2: Just minutes as number
    try:
        total_minutes = int(s)
        if total_minutes <= 0:
            return ""

        hours, minutes = divmod(total_minutes, 60)
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        return f"{minutes}мин"
    except ValueError:
        return s  # Return as-is if not a number


def format_movie_card(movie: Movie) -> str:
    """
    Format movie information as HTML message.

    Args:
        movie: Movie object with all details

    Returns:
        Formatted HTML string
    """
    lines = []

    # Title with year
    if movie.year:
        lines.append(f"<b>{movie.title}</b> ({movie.year})")
    else:
        lines.append(f"<b>{movie.title}</b>")

    # Original title and duration
    meta_parts = []
    if movie.original_title and movie.original_title != movie.title:
        meta_parts.append(movie.original_title)
    if movie.duration:
        duration_str = format_duration(movie.duration)
        if duration_str:
            meta_parts.append(duration_str)
    if meta_parts:
        lines.append(", ".join(meta_parts))

    # Rating
    if movie.rating and movie.rating not in ("None", "null", "—", ""):
        lines.append(f"⭐ Рейтинг: {movie.rating}")

    lines.append("")  # Empty line

    # Countries and genres
    info_parts = []
    if movie.countries:
        info_parts.append(", ".join(movie.countries[:2]))
    if movie.genres:
        info_parts.append(", ".join(movie.genres[:3]))
    if info_parts:
        lines.append(" • ".join(info_parts))

    # Staff
    if movie.directors:
        lines.append(f"🎬 Режиссёр: {', '.join(movie.directors[:2])}")
    if movie.actors:
        lines.append(f"🎭 В ролях: {', '.join(movie.actors[:5])}")

    # Description
    if movie.description:
        desc = movie.description
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            desc = desc[:MAX_DESCRIPTION_LENGTH].rsplit(" ", 1)[0] + "..."
        lines.append(f"\n{desc}")

    return "\n".join(lines)
