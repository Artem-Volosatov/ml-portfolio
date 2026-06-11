"""
FastAPI приложение - эндпоинты API.
"""

from fastapi import FastAPI, HTTPException

from app.schemas import (
    FitRequest, PredictRequest, ModelNameRequest,
    MessageResponse, PredictResponse, StatusResponse,
    FitResponse, TaskStatusResponse, TaskStatus
)
from app.ml_models import SUPPORTED_MODEL_TYPES
from app import storage
from app.config import MODEL_DIR, MAX_TRAINING_PROCESSES, MAX_LOADED_MODELS
from app.process_manager import process_manager
from app.training import train_model_task


# ==================== FASTAPI ПРИЛОЖЕНИЕ ====================

app = FastAPI(
    title="ML Model Server",
    description="Сервер для обучения и инференса ML моделей",
    version="0.4.0"
)


# ==================== ЭНДПОИНТЫ ====================

@app.post("/fit", response_model=FitResponse)
def fit(request: FitRequest):
    """
    Запустить обучение модели в фоновом процессе.
    """

    # Проверка: модель уже существует?
    if storage.model_exists_on_disk(request.model_name):
        raise HTTPException(
            400, f"Модель '{request.model_name}' уже существует")

    # Проверка: есть ли свободные процессы?
    if not process_manager.can_submit():
        raise HTTPException(
            503,
            f"Нет свободных процессов. Активно: {process_manager.get_active_count()}/{MAX_TRAINING_PROCESSES}"
        )

    # Запускаем обучение в отдельном процессе
    try:
        task_id = process_manager.submit(
            train_model_task,
            task_model_name=request.model_name,  # ← ДЛЯ ТРЕКИНГА ЗАДАЧИ
            # Аргументы для train_model_task:
            model_dir=MODEL_DIR,
            model_name=request.model_name,       # ← ДЛЯ ФУНКЦИИ ОБУЧЕНИЯ
            model_type=request.model_type,
            X=request.X,
            y=request.y,
            hyperparameters=request.hyperparameters
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    return FitResponse(
        task_id=task_id,
        message=f"Обучение модели '{request.model_name}' запущено"
    )


@app.get("/fit/status/{task_id}", response_model=TaskStatusResponse)
def fit_status(task_id: str):
    """Получить статус задачи обучения"""

    task = process_manager.get_task_status(task_id)

    if task is None:
        raise HTTPException(404, f"Задача '{task_id}' не найдена")

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        model_name=task.model_name,
        error=task.error
    )


@app.post("/load", response_model=MessageResponse)
def load(request: ModelNameRequest):
    """Загрузить модель в память для инференса"""

    # Проверка: модель существует на диске?
    if not storage.model_exists_on_disk(request.model_name):
        raise HTTPException(404, f"Модель '{request.model_name}' не найдена на диске")

    # Проверка: модель уже загружена?
    if storage.is_model_loaded(request.model_name):
        raise HTTPException(400, f"Модель '{request.model_name}' уже загружена")

    # Проверка лимита загруженных моделей
    if not storage.can_load_more():
        raise HTTPException(
            503,
            f"Достигнут лимит загруженных моделей ({MAX_LOADED_MODELS}). "
            f"Выгрузите одну из моделей через /unload"
        )

    # Загружаем
    model_data = storage.load_model_from_disk(request.model_name)
    storage.add_loaded_model(request.model_name, model_data)

    model_type = model_data.get("model_type", "unknown")
    return MessageResponse(
        message=f"Модель '{request.model_name}' (тип: {model_type}) загружена"
    )


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """Предсказание с помощью загруженной модели"""

    if not storage.is_model_loaded(request.model_name):
        raise HTTPException(
            400,
            f"Модель '{request.model_name}' не загружена. Сначала вызовите /load"
        )

    model_data = storage.get_loaded_model(request.model_name)
    model = model_data["model"]
    predictions = model.predict(request.X)

    return PredictResponse(predictions=predictions.tolist())


@app.post("/unload", response_model=MessageResponse)
def unload(request: ModelNameRequest):
    """Выгрузить модель из памяти"""

    if not storage.is_model_loaded(request.model_name):
        raise HTTPException(400, f"Модель '{request.model_name}' не загружена")

    storage.remove_loaded_model(request.model_name)

    return MessageResponse(message=f"Модель '{request.model_name}' выгружена")


@app.post("/remove", response_model=MessageResponse)
def remove(request: ModelNameRequest):
    """Удалить модель с диска"""

    if not storage.model_exists_on_disk(request.model_name):
        raise HTTPException(404, f"Модель '{request.model_name}' не найдена")

    storage.remove_loaded_model(request.model_name)
    storage.delete_model_from_disk(request.model_name)

    return MessageResponse(message=f"Модель '{request.model_name}' удалена")


@app.post("/remove_all", response_model=MessageResponse)
def remove_all():
    """Удалить все модели с диска"""

    storage.clear_loaded_models()
    count = storage.delete_all_models_from_disk()

    return MessageResponse(message=f"Удалено моделей: {count}")


@app.get("/status", response_model=StatusResponse)
def status():
    """Статус сервера"""
    return StatusResponse(
        loaded_models=storage.get_loaded_models_info(),
        models_on_disk=storage.get_models_on_disk_info(),
        supported_model_types=SUPPORTED_MODEL_TYPES,
        active_training_tasks=process_manager.get_active_count(),
        max_training_processes=MAX_TRAINING_PROCESSES,
        max_loaded_models=MAX_LOADED_MODELS
    )


# ==================== СОБЫТИЯ ЖИЗНЕННОГО ЦИКЛА ====================

@app.on_event("shutdown")
def shutdown_event():
    """Корректное завершение при остановке сервера"""
    process_manager.shutdown()
