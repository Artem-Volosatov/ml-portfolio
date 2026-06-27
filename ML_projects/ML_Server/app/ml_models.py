"""
ML модели и фабрика для их создания.
"""

from typing import Dict, Any, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from app.schemas import ModelType


def create_model(model_type: ModelType, hyperparameters: Optional[Dict[str, Any]] = None):
    """
    Фабрика для создания ML моделей.

    Args:
        model_type: Тип модели ('random_forest', 'gradient_boosting', 'logistic_regression')
        hyperparameters: Словарь гиперпараметров

    Returns:
        Экземпляр sklearn модели

    Raises:
        ValueError: Если тип модели неизвестен
    """
    params = hyperparameters or {}

    if model_type == "random_forest":
        default_params = {
            "n_estimators": 100,
            "max_depth": None,
            "random_state": 42
        }
        default_params.update(params)
        return RandomForestClassifier(**default_params)

    elif model_type == "gradient_boosting":
        default_params = {
            "n_estimators": 100,
            "max_depth": 3,
            "learning_rate": 0.1,
            "random_state": 42
        }
        default_params.update(params)
        return GradientBoostingClassifier(**default_params)

    elif model_type == "logistic_regression":
        default_params = {
            "max_iter": 1000,
            "random_state": 42
        }
        default_params.update(params)
        return LogisticRegression(**default_params)

    else:
        raise ValueError(f"Неизвестный тип модели: {model_type}")


# Список поддерживаемых типов моделей
SUPPORTED_MODEL_TYPES = ["random_forest",
                         "gradient_boosting", "logistic_regression"]
