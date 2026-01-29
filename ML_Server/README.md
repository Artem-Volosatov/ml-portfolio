# ML Model Server

Многозадачный веб-сервер для обучения и инференса ML моделей.

## 🚀 Возможности

- Обучение моделей в фоновых процессах
- Параллельное обучение нескольких моделей
- Ограничение по числу процессов обучения
- Загрузка/выгрузка моделей для инференса
- Ограничение по числу загруженных моделей
- REST API на FastAPI
- Поддержка Docker

## 📦 Поддерживаемые модели

| Тип | Класс sklearn |
|-----|---------------|
| `random_forest` | RandomForestClassifier |
| `gradient_boosting` | GradientBoostingClassifier |
| `logistic_regression` | LogisticRegression |

## 🛠 Установка и запуск

### Локальный запуск

```bash
# Клонировать репозиторий
git clone <url>
cd ml-server

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
python run_server.py
```

### Запуск в Docker

```bash
# Собрать и запустить
docker-compose up --build

# Или в фоновом режиме
docker-compose up --build -d

# Остановить
docker-compose down
```

## ⚙️ Конфигурация

Настройки задаются через переменные окружения или файл `.env`:

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `MODEL_STORAGE_PATH` | `./models` | Путь для сохранения моделей |
| `MAX_CORES` | `4` | Общее число ядер (включая серверное) |
| `MAX_LOADED_MODELS` | `10` | Максимум моделей в памяти для инференса |

Пример `.env`:
```env
MODEL_STORAGE_PATH=/app/models
MAX_CORES=4
MAX_LOADED_MODELS=10
```

## 📡 API Endpoints

### Обучение

#### `POST /fit`
Запустить обучение модели.

**Request:**
```json
{
  "model_name": "my_model",
  "model_type": "random_forest",
  "X": , ],
  "y": ,
  "hyperparameters": {"n_estimators": 100}
}
```

**Response:**
```json
{
  "task_id": "abc12345",
  "message": "Обучение модели 'my_model' запущено"
}
```

#### `GET /fit/status/{task_id}`
Проверить статус обучения.

**Response:**
```json
{
  "task_id": "abc12345",
  "status": "completed",
  "model_name": "my_model",
  "error": null
}
```

Статусы: `pending`, `completed`, `failed`

### Инференс

#### `POST /load`
Загрузить модель в память.

```json
{"model_name": "my_model"}
```

#### `POST /predict`
Сделать предсказание.

**Request:**
```json
{
  "model_name": "my_model",
  "X": , ]
}
```

**Response:**
```json
{
  "predictions":
}
```

#### `POST /unload`
Выгрузить модель из памяти.

```json
{"model_name": "my_model"}
```

### Управление моделями

#### `POST /remove`
Удалить модель с диска.

```json
{"model_name": "my_model"}
```

#### `POST /remove_all`
Удалить все модели.

### Статус

#### `GET /status`
Получить статус сервера.

**Response:**
```json
{
  "loaded_models": ,
  "models_on_disk": ,
  "supported_model_types": ,
  "active_training_tasks": 1,
  "max_training_processes": 3,
  "max_loaded_models": 10
}
```

## 🔴 Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Некорректный запрос (модель уже существует, не загружена и т.д.) |
| 404 | Модель не найдена |
| 503 | Нет свободных ресурсов (процессов или слотов для загрузки) |

## 📁 Структура проекта

```
ml-server/
├── app/
│   ├── __init__.py
│   ├── config.py           # Конфигурация
│   ├── main.py             # FastAPI endpoints
│   ├── ml_models.py        # Фабрика ML моделей
│   ├── process_manager.py  # Управление процессами
│   ├── schemas.py          # Pydantic схемы
│   ├── storage.py          # Хранение моделей
│   └── training.py         # Функция обучения
├── models/                 # Сохранённые модели
├── .env                    # Конфигурация
├── async_client.py         # Асинхронный клиент (aiohttp)
├── client.py               # Синхронный клиент (requests)
├── demo.ipynb              # Jupyter демонстрация
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run_server.py           # Точка входа
└── README.md
```

## 🧪 Демонстрация

### Синхронный клиент
```bash
python client.py
```

### Асинхронный клиент
```bash
python async_client.py
```

### Jupyter Notebook
```bash
jupyter notebook demo.ipynb
```

## 📊 Пример использования

```python
import requests

BASE_URL = "http://localhost:8000"

# Обучение
response = requests.post(f"{BASE_URL}/fit", json={
    "model_name": "my_model",
    "model_type": "random_forest",
    "X": , , ],
    "y":
})
task_id = response.json()

# Ожидание завершения
import time
while True:
    status = requests.get(f"{BASE_URL}/fit/status/{task_id}").json()
    if status != "pending":
        break
    time.sleep(1)

# Загрузка и предсказание
requests.post(f"{BASE_URL}/load", json={"model_name": "my_model"})
predictions = requests.post(f"{BASE_URL}/predict", json={
    "model_name": "my_model",
    "X": ]
}).json()

print(predictions)  #  или
```