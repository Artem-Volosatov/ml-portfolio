# Базовый образ
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/
COPY run_server.py .

# Создаём директорию для моделей
RUN mkdir -p /app/models

# Порт
EXPOSE 8000

# Запуск
CMD ["python", "run_server.py"]
