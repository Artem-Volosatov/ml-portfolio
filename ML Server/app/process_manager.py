"""
Менеджер процессов обучения.
Отслеживает активные задачи и контролирует лимиты.
"""

from concurrent.futures import ProcessPoolExecutor, Future
from typing import Dict, Optional
import uuid
from dataclasses import dataclass

from app.config import MAX_TRAINING_PROCESSES
from app.schemas import TaskStatus


@dataclass
class TrainingTask:
    """Информация о задаче обучения"""
    task_id: str
    model_name: str
    future: Future
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None


class ProcessManager:
    """
    Менеджер процессов обучения.
    """

    def __init__(self, max_workers: int = MAX_TRAINING_PROCESSES):
        self.max_workers = max_workers
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TrainingTask] = {}

    def get_active_count(self) -> int:
        """Количество активных (незавершённых) задач"""
        self._update_task_statuses()
        return sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)

    def can_submit(self) -> bool:
        """Можно ли запустить новую задачу?"""
        return self.get_active_count() < self.max_workers

    def submit(self, func, task_model_name: str, *args, **kwargs) -> str:
        """
        Запустить задачу обучения.

        Args:
            func: Функция для выполнения
            task_model_name: Имя модели (для отслеживания задачи)  # ← ПЕРЕИМЕНОВАНО
            *args, **kwargs: Аргументы для func

        Returns:
            task_id
        """
        if not self.can_submit():
            raise RuntimeError("Нет свободных процессов для обучения")

        task_id = str(uuid.uuid4())[:8]
        future = self.executor.submit(func, *args, **kwargs)

        self.tasks[task_id] = TrainingTask(
            task_id=task_id,
            model_name=task_model_name,  # ← ИЗМЕНЕНО
            future=future,
            status=TaskStatus.PENDING
        )

        return task_id

    def get_task_status(self, task_id: str) -> Optional[TrainingTask]:
        """Получить статус задачи"""
        self._update_task_statuses()
        return self.tasks.get(task_id)

    def _update_task_statuses(self):
        """Обновить статусы всех задач"""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and task.future.done():
                try:
                    result = task.future.result()
                    if result.get("success"):
                        task.status = TaskStatus.COMPLETED
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = result.get("error", "Unknown error")
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)

    def shutdown(self):
        """Завершить работу executor'а"""
        self.executor.shutdown(wait=False)


# Глобальный экземпляр
process_manager = ProcessManager()
