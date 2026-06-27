"""
Хранение моделей: работа с диском и реестр загруженных моделей.
"""

import os
import joblib
from typing import Dict, Any, List, Optional

from app.config import MODEL_DIR, MAX_LOADED_MODELS
from app.schemas import ModelInfo


# ==================== РЕЕСТР ЗАГРУЖЕННЫХ МОДЕЛЕЙ ====================

_loaded_models: Dict[str, Dict[str, Any]] = {}


def get_loaded_models() -> Dict[str, Dict[str, Any]]:
    """Получить словарь загруженных моделей"""
    return _loaded_models


def get_loaded_count() -> int:
    """Получить количество загруженных моделей"""
    return len(_loaded_models)


def can_load_more() -> bool:
    """Можно ли загрузить ещё одну модель?"""
    return get_loaded_count() < MAX_LOADED_MODELS


def is_model_loaded(model_name: str) -> bool:
    """Проверить, загружена ли модель в память"""
    return model_name in _loaded_models


def get_loaded_model(model_name: str) -> Optional[Dict[str, Any]]:
    """Получить загруженную модель по имени"""
    return _loaded_models.get(model_name)


def add_loaded_model(model_name: str, model_data: Dict[str, Any]) -> None:
    """Добавить модель в реестр загруженных"""
    _loaded_models[model_name] = model_data


def remove_loaded_model(model_name: str) -> None:
    """Удалить модель из реестра загруженных"""
    if model_name in _loaded_models:
        del _loaded_models[model_name]


def clear_loaded_models() -> None:
    """Очистить все загруженные модели"""
    _loaded_models.clear()


def get_loaded_models_info() -> List[ModelInfo]:
    """Получить информацию о загруженных моделях"""
    return [
        ModelInfo(name=name, type=data.get("model_type", "unknown"))
        for name, data in _loaded_models.items()
    ]


# ==================== РАБОТА С ДИСКОМ ====================

def get_model_path(model_name: str) -> str:
    """Получить путь к файлу модели"""
    return os.path.join(MODEL_DIR, f"{model_name}.joblib")


def model_exists_on_disk(model_name: str) -> bool:
    """Проверить, существует ли модель на диске"""
    return os.path.exists(get_model_path(model_name))


def save_model_to_disk(model_name: str, model: Any, model_type: str,
                       hyperparameters: Optional[Dict[str, Any]] = None) -> None:
    """Сохранить модель на диск"""
    model_data = {
        "model": model,
        "model_type": model_type,
        "hyperparameters": hyperparameters
    }
    joblib.dump(model_data, get_model_path(model_name))


def load_model_from_disk(model_name: str) -> Dict[str, Any]:
    """Загрузить модель с диска"""
    return joblib.load(get_model_path(model_name))


def delete_model_from_disk(model_name: str) -> None:
    """Удалить модель с диска"""
    os.remove(get_model_path(model_name))


def get_all_models_on_disk() -> List[str]:
    """Получить список имён всех моделей на диске"""
    return [
        f.replace(".joblib", "")
        for f in os.listdir(MODEL_DIR)
        if f.endswith(".joblib")
    ]


def get_models_on_disk_info() -> List[ModelInfo]:
    """Получить информацию о моделях на диске"""
    result = []
    for model_name in get_all_models_on_disk():
        try:
            model_data = load_model_from_disk(model_name)
            model_type = model_data.get("model_type", "unknown")
        except Exception:
            model_type = "unknown"
        result.append(ModelInfo(name=model_name, type=model_type))
    return result


def delete_all_models_from_disk() -> int:
    """Удалить все модели с диска. Возвращает количество удалённых."""
    count = 0
    for model_name in get_all_models_on_disk():
        delete_model_from_disk(model_name)
        count += 1
    return count
