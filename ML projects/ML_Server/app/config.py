"""
Конфигурация сервера.
Загружается из переменных окружения / .env файла.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Настройки сервера.
    Загружаются из переменных окружения или .env файла.
    """

    # Убираем warning про protected namespace
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=()  # Отключаем защиту namespace
    )

    # Путь к директории для сохранения моделей
    model_storage_path: str = "./models"

    # Максимальное число ядер (включая серверное)
    max_cores: int = 4

    # Максимум загруженных моделей для инференса
    max_loaded_models: int = 10

    @property
    def max_training_processes(self) -> int:
        """Число ядер для обучения (одно всегда для сервера)"""
        return max(1, self.max_cores - 1)


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (с кэшированием)."""
    return Settings()


# Создаём директорию для моделей при импорте
settings = get_settings()
os.makedirs(settings.model_storage_path, exist_ok=True)

# Для обратной совместимости
MODEL_DIR = settings.model_storage_path
MAX_CORES = settings.max_cores
MAX_TRAINING_PROCESSES = settings.max_training_processes
MAX_LOADED_MODELS = settings.max_loaded_models
