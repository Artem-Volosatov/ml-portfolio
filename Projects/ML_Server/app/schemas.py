"""
Pydantic схемы для запросов и ответов API.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


# Доступные типы моделей
ModelType = Literal["random_forest",
                    "gradient_boosting", "logistic_regression"]


# ==================== Статусы задач ====================

class TaskStatus(str, Enum):
    """Статус задачи обучения"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== BASE CONFIG (убирает warning) ====================

class BaseSchema(BaseModel):
    """Базовая схема с отключенной защитой namespace model_"""
    model_config = ConfigDict(protected_namespaces=())


# ==================== REQUEST СХЕМЫ ====================

class FitRequest(BaseSchema):
    """Запрос на обучение модели"""
    model_name: str
    model_type: ModelType = "random_forest"
    X: List[List[float]]
    y: List[float]
    hyperparameters: Optional[Dict[str, Any]] = None


class PredictRequest(BaseSchema):
    """Запрос на предсказание"""
    model_name: str
    X: List[List[float]]


class ModelNameRequest(BaseSchema):
    """Запрос с именем модели"""
    model_name: str


# ==================== RESPONSE СХЕМЫ ====================

class MessageResponse(BaseModel):
    """Простой ответ с сообщением"""
    message: str


class PredictResponse(BaseModel):
    """Ответ с предсказаниями"""
    predictions: List[float]


class ModelInfo(BaseSchema):
    """Информация о модели"""
    name: str
    type: str


class FitResponse(BaseModel):
    """Ответ на запрос обучения"""
    task_id: str
    message: str


class TaskStatusResponse(BaseSchema):
    """Статус задачи обучения"""
    task_id: str
    status: TaskStatus
    model_name: Optional[str] = None
    error: Optional[str] = None


class StatusResponse(BaseSchema):
    """Статус сервера"""
    loaded_models: List[ModelInfo]
    models_on_disk: List[ModelInfo]
    supported_model_types: List[str]
    active_training_tasks: int
    max_training_processes: int
    max_loaded_models: int  # НОВОЕ
