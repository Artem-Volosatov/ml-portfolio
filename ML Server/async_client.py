"""
Асинхронный клиент для ML Model Server.
Демонстрация работы с aiohttp.
"""

import asyncio
import aiohttp
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


# ==================== ASYNC API ФУНКЦИИ ====================

async def fit_model_async(session: aiohttp.ClientSession, model_name: str,
                          X, y, model_type: str = "random_forest",
                          hyperparameters: dict = None):
    """Асинхронный запуск обучения модели"""
    payload = {
        "model_name": model_name,
        "model_type": model_type,
        "X": X,
        "y": y
    }
    if hyperparameters:
        payload["hyperparameters"] = hyperparameters

    async with session.post(f"{BASE_URL}/fit", json=payload) as response:
        result = await response.json()
        print(f"FIT [{model_type}] {model_name}: {response.status} - task_id: {result.get('task_id')}")
        return result


async def get_fit_status_async(session: aiohttp.ClientSession, task_id: str):
    """Асинхронная проверка статуса обучения"""
    async with session.get(f"{BASE_URL}/fit/status/{task_id}") as response:
        return await response.json()


async def wait_for_training_async(session: aiohttp.ClientSession, task_id: str,
                                   model_name: str, timeout: int = 300):
    """Асинхронное ожидание завершения обучения"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        result = await get_fit_status_async(session, task_id)
        status = result.get("status")

        if status == "completed":
            print(f"  ✓ Модель '{model_name}' обучена успешно")
            return True
        elif status == "failed":
            print(f"  ✗ Ошибка обучения '{model_name}': {result.get('error')}")
            return False

        await asyncio.sleep(1)

    print(f"  ✗ Таймаут обучения '{model_name}'")
    return False


async def load_model_async(session: aiohttp.ClientSession, model_name: str):
    """Асинхронная загрузка модели"""
    async with session.post(f"{BASE_URL}/load", json={"model_name": model_name}) as response:
        result = await response.json()
        print(f"LOAD {model_name}: {response.status}")
        return result


async def predict_async(session: aiohttp.ClientSession, model_name: str, X):
    """Асинхронное предсказание"""
    async with session.post(f"{BASE_URL}/predict", json={"model_name": model_name, "X": X}) as response:
        result = await response.json()
        return result


async def unload_model_async(session: aiohttp.ClientSession, model_name: str):
    """Асинхронная выгрузка модели"""
    async with session.post(f"{BASE_URL}/unload", json={"model_name": model_name}) as response:
        result = await response.json()
        print(f"UNLOAD {model_name}: {response.status}")
        return result


async def remove_all_async(session: aiohttp.ClientSession):
    """Асинхронное удаление всех моделей"""
    async with session.post(f"{BASE_URL}/remove_all") as response:
        result = await response.json()
        print(f"REMOVE_ALL: {response.status} - {result}")
        return result


async def get_status_async(session: aiohttp.ClientSession):
    """Асинхронное получение статуса"""
    async with session.get(f"{BASE_URL}/status") as response:
        result = await response.json()
        print(f"STATUS: active_training={result['active_training_tasks']}/{result['max_training_processes']}, "
              f"loaded={len(result['loaded_models'])}/{result['max_loaded_models']}")
        return result


# ==================== ДЕМОНСТРАЦИИ ====================

async def demo_parallel_training():
    """Демонстрация параллельного обучения с aiohttp"""
    print("\n" + "=" * 60)
    print("АСИНХРОННОЕ ПАРАЛЛЕЛЬНОЕ ОБУЧЕНИЕ (aiohttp)")
    print("=" * 60)

    X, y = generate_data(n_samples=5000, n_features=50)

    models = [
        ("async_rf", "random_forest", {"n_estimators": 200}),
        ("async_gb", "gradient_boosting", {"n_estimators": 200}),
    ]

    async with aiohttp.ClientSession() as session:
        # Очистка
        await remove_all_async(session)

        start_time = time.time()

        # Запускаем ВСЕ обучения одновременно
        print("\n--- Запуск всех обучений одновременно ---")
        fit_tasks = []
        for model_name, model_type, params in models:
            task = fit_model_async(session, model_name, X, y, model_type, params)
            fit_tasks.append(task)

        # Ждём запуска всех
        results = await asyncio.gather(*fit_tasks)

        # Собираем task_ids
        task_ids = [(r.get("task_id"), models[i][0]) for i, r in enumerate(results) if r.get("task_id")]

        # Статус
        await get_status_async(session)

        # Ждём завершения всех (тоже параллельно!)
        print("\n--- Ожидание завершения (параллельно) ---")
        wait_tasks = [
            wait_for_training_async(session, task_id, model_name)
            for task_id, model_name in task_ids
        ]
        await asyncio.gather(*wait_tasks)

        total_time = time.time() - start_time
        print(f"\n>>> ОБЩЕЕ ВРЕМЯ (async): {total_time:.2f} сек")

        # Очистка
        await remove_all_async(session)

        return total_time


async def demo_parallel_predictions():
    """Демонстрация параллельных предсказаний"""
    print("\n" + "=" * 60)
    print("АСИНХРОННЫЕ ПАРАЛЛЕЛЬНЫЕ ПРЕДСКАЗАНИЯ")
    print("=" * 60)

    X, y = generate_data(n_samples=500)
    X_test = X[:100]

    async with aiohttp.ClientSession() as session:
        # Очистка и подготовка
        await remove_all_async(session)

        # Обучаем модель (быстро)
        print("\n--- Обучение модели ---")
        result = await fit_model_async(session, "pred_model", X, y, "logistic_regression")
        task_id = result.get("task_id")
        if task_id:
            await wait_for_training_async(session, task_id, "pred_model")

        # Загружаем
        await load_model_async(session, "pred_model")

        # Параллельные предсказания
        print("\n--- Параллельные предсказания (10 запросов) ---")
        start_time = time.time()

        # Создаём 10 задач предсказания
        predict_tasks = [
            predict_async(session, "pred_model", X_test)
            for _ in range(10)
        ]

        # Выполняем все параллельно
        results = await asyncio.gather(*predict_tasks)

        elapsed = time.time() - start_time
        print(f"  Выполнено {len(results)} предсказаний за {elapsed:.2f} сек")
        print(f"  Среднее время на запрос: {elapsed/len(results)*1000:.1f} мс")

        # Очистка
        await remove_all_async(session)


async def main():
    """Главная функция демонстрации"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ АСИНХРОННОГО КЛИЕНТА (aiohttp)")
    print("=" * 60)

    # 1. Параллельное обучение
    await demo_parallel_training()

    # 2. Параллельные предсказания
    await demo_parallel_predictions()

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
