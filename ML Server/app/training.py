"""
Функция обучения модели.
Выделена в отдельный модуль, чтобы быть picklable для ProcessPoolExecutor.
"""

from typing import Dict, Any, Optional, List
import joblib
import os


def train_model_task(
    model_dir: str,
    model_name: str,
    model_type: str,
    X: List[List[float]],
    y: List[float],
    hyperparameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Функция обучения модели, выполняется в отдельном процессе.

    ВАЖНО: Эта функция должна быть самодостаточной (все импорты внутри),
    чтобы корректно работать в subprocess.

    Args:
        model_dir: Путь к директории для сохранения
        model_name: Имя модели
        model_type: Тип модели
        X: Обучающие данные
        y: Метки
        hyperparameters: Гиперпараметры

    Returns:
        Словарь с результатом {"success": bool, "error": str or None}
    """
    try:
        # Импорты внутри функции для pickling
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression

        # Создаём модель
        params = hyperparameters or {}

        if model_type == "random_forest":
            default_params = {"n_estimators": 100,
                              "max_depth": None, "random_state": 42}
            default_params.update(params)
            model = RandomForestClassifier(**default_params)

        elif model_type == "gradient_boosting":
            default_params = {"n_estimators": 100, "max_depth": 3,
                              "learning_rate": 0.1, "random_state": 42}
            default_params.update(params)
            model = GradientBoostingClassifier(**default_params)

        elif model_type == "logistic_regression":
            default_params = {"max_iter": 1000, "random_state": 42}
            default_params.update(params)
            model = LogisticRegression(**default_params)

        else:
            return {"success": False, "error": f"Неизвестный тип модели: {model_type}"}

        # Обучаем
        model.fit(X, y)

        # Сохраняем
        model_data = {
            "model": model,
            "model_type": model_type,
            "hyperparameters": hyperparameters
        }
        model_path = os.path.join(model_dir, f"{model_name}.joblib")
        joblib.dump(model_data, model_path)

        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": str(e)}
