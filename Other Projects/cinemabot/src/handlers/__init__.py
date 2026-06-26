"""Handlers package - exports all routers."""

from src.handlers.commands import router as commands_router
from src.handlers.search import router as search_router
from src.handlers.stats import router as stats_router

# Order matters: commands first, then specific handlers, search last (catches all text)
routers = [
    commands_router,
    stats_router,
    search_router,
]

__all__ = ["routers"]
