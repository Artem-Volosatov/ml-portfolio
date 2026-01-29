"""
ML Model Client — Демонстрация работы с сервером.
Этап 3b: Параллельное обучение
"""

import requests
import time
from sklearn.datasets import make_classification

BASE_URL = "http://localhost:8000"


def generate_data(n_samples=1000, n_features=20):
    """Генерация тестовых данных"""
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=10,
        random_state=42
    )
    return X.tolist(), y.tolist()


# ==================== API ФУНКЦИИ ====================

def fit_model(model_name: str, X, y, model_type: str = "random_forest", hyperparameters: dict = None):
    """Запустить обучение модели (неблокирующее)"""
    payload = {
        "model_name": model_name,
        "model_type": model_type,
        "X": X,
        "y": y
    }
    if hyperparameters:
        payload["hyperparameters"] = hyperparameters

    response = requests.post(f"{BASE_URL}/fit", json=payload)
    result = response.json()
    print(f"FIT [{model_type}]: {response.status_code} - {result}")
    return response


def get_fit_status(task_id: str):
    """Проверить статус обучения"""
    response = requests.get(f"{BASE_URL}/fit/status/{task_id}")
    return response


def wait_for_training(task_id: str, model_name: str, timeout: int = 300, poll_interval: float = 1.0):
    """
    Ожидать завершения обучения.

    Args:
        task_id: ID задачи
        model_name: Имя модели (для логов)
        timeout: Максимальное время ожидания (сек)
        poll_interval: Интервал опроса (сек)

    Returns:
        True если успешно, False если ошибка
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = get_fit_status(task_id)
        result = response.json()
        status = result.get("status")

        if status == "completed":
            print(f"  ✓ Модель '{model_name}' обучена успешно")
            return True
        elif status == "failed":
            print(f"  ✗ Ошибка обучения '{model_name}': {result.get('error')}")
            return False

        # Ещё в процессе
        time.sleep(poll_interval)

    print(f"  ✗ Таймаут обучения '{model_name}'")
    return False


def load_model(model_name: str):
    """Загрузить модель"""
    response = requests.post(
        f"{BASE_URL}/load", json={"model_name": model_name})
    print(f"LOAD: {response.status_code} - {response.json()}")
    return response


def predict(model_name: str, X):
    """Предсказание"""
    response = requests.post(f"{BASE_URL}/predict", json={
        "model_name": model_name,
        "X": X
    })
    result = response.json()
    if "predictions" in result:
        preview = result["predictions"][:5]
        print(f"PREDICT: {response.status_code} - первые 5: {preview}")
    else:
        print(f"PREDICT: {response.status_code} - {result}")
    return response


def unload_model(model_name: str):
    """Выгрузить модель"""
    response = requests.post(f"{BASE_URL}/unload",
                             json={"model_name": model_name})
    print(f"UNLOAD: {response.status_code} - {response.json()}")
    return response


def remove_model(model_name: str):
    """Удалить модель"""
    response = requests.post(f"{BASE_URL}/remove",
                             json={"model_name": model_name})
    print(f"REMOVE: {response.status_code} - {response.json()}")
    return response


def remove_all_models():
    """Удалить все модели"""
    response = requests.post(f"{BASE_URL}/remove_all")
    print(f"REMOVE_ALL: {response.status_code} - {response.json()}")
    return response


def get_status():
    """Статус сервера"""
    response = requests.get(f"{BASE_URL}/status")
    result = response.json()
    print(f"STATUS:")
    print(f"  Загружено моделей: {result['loaded_models']}")
    print(f"  Моделей на диске: {result['models_on_disk']}")
    print(
        f"  Активных обучений: {result['active_training_tasks']}/{result['max_training_processes']}")
    return response


# ==================== ДЕМОНСТРАЦИЯ ====================

def demo_sequential_training():
    """Демонстрация последовательного обучения"""
    print("\n" + "=" * 60)
    print("ПОСЛЕДОВАТЕЛЬНОЕ ОБУЧЕНИЕ (одна за другой)")
    print("=" * 60)

    # Большой датасет для долгого обучения
    X, y = generate_data(n_samples=5000, n_features=50)

    models = [
        ("seq_rf", "random_forest", {"n_estimators": 200}),
        ("seq_gb", "gradient_boosting", {"n_estimators": 200}),
    ]

    start_time = time.time()

    for model_name, model_type, params in models:
        print(f"\n--- Обучение {model_name} ---")
        model_start = time.time()

        # Запускаем обучение
        response = fit_model(model_name, X, y, model_type, params)
        task_id = response.json().get("task_id")

        if task_id:
            # Ждём завершения
            wait_for_training(task_id, model_name)

        print(f"  Время: {time.time() - model_start:.2f} сек")

    total_time = time.time() - start_time
    print(f"\n>>> ОБЩЕЕ ВРЕМЯ (последовательно): {total_time:.2f} сек")
    return total_time


def demo_parallel_training():
    """Демонстрация параллельного обучения"""
    print("\n" + "=" * 60)
    print("ПАРАЛЛЕЛЬНОЕ ОБУЧЕНИЕ (одновременно)")
    print("=" * 60)

    # Тот же датасет
    X, y = generate_data(n_samples=5000, n_features=50)

    models = [
        ("par_rf", "random_forest", {"n_estimators": 200}),
        ("par_gb", "gradient_boosting", {"n_estimators": 200}),
    ]

    start_time = time.time()

    # Запускаем ВСЕ обучения сразу
    tasks = []
    for model_name, model_type, params in models:
        print(f"\n--- Запуск {model_name} ---")
        response = fit_model(model_name, X, y, model_type, params)
        task_id = response.json().get("task_id")
        if task_id:
            tasks.append((task_id, model_name))

    # Показываем статус
    print("\n--- Статус после запуска всех ---")
    get_status()

    # Ждём завершения ВСЕХ
    print("\n--- Ожидание завершения ---")
    for task_id, model_name in tasks:
        wait_for_training(task_id, model_name)

    total_time = time.time() - start_time
    print(f"\n>>> ОБЩЕЕ ВРЕМЯ (параллельно): {total_time:.2f} сек")
    return total_time


def demo_basic_operations():
    """Демонстрация базовых операций"""
    print("\n" + "=" * 60)
    print("БАЗОВЫЕ ОПЕРАЦИИ")
    print("=" * 60)

    X, y = generate_data(500)
    X_test = X[:5]

    # Обучаем простую модель
    print("\n--- Быстрое обучение ---")
    response = fit_model("test_model", X, y, "logistic_regression")
    task_id = response.json().get("task_id")
    if task_id:
        wait_for_training(task_id, "test_model")

    # Загружаем
    print("\n--- Загрузка ---")
    load_model("test_model")

    # Предсказание
    print("\n--- Предсказание ---")
    predict("test_model", X_test)

    # Выгрузка
    print("\n--- Выгрузка ---")
    unload_model("test_model")

    # Статус
    print("\n--- Статус ---")
    get_status()


if __name__ == "__main__":
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ML MODEL SERVER")
    print("=" * 60)

    # Очистка
    print("\n--- Подготовка: очистка ---")
    remove_all_models()
    get_status()

    # 1. Базовые операции
    demo_basic_operations()

    # Очистка перед сравнением
    print("\n--- Очистка перед сравнением ---")
    remove_all_models()

    # 2. Последовательное обучение
    seq_time = demo_sequential_training()

    # Очистка
    remove_all_models()

    # 3. Параллельное обучение
    par_time = demo_parallel_training()

    # Итог
    print("\n" + "=" * 60)
    print("ИТОГИ СРАВНЕНИЯ")
    print("=" * 60)
    print(f"Последовательно: {seq_time:.2f} сек")
    print(f"Параллельно:     {par_time:.2f} сек")
    if seq_time > 0:
        print(f"Ускорение:       {seq_time / par_time:.2f}x")

    # Финальная очистка
    print("\n--- Финальная очистка ---")
    remove_all_models()
    get_status()

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
