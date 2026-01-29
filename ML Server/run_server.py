"""
Точка входа для запуска сервера.
Запуск: python run_server.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting ML Model Server...")
    print(f"  Model storage: {settings.model_storage_path}")
    print(f"  Max cores: {settings.max_cores}")
    print(f"  Max training processes: {settings.max_training_processes}")
    print(f"  Max loaded models: {settings.max_loaded_models}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Убрать в продакшене
    )
