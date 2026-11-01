# 🔗 URL Shortener Service (Сервис сокращения ссылок)

Высокопроизводительный сервис для сокращения длинных URL-адресов, выполнения редиректов и сбора статистики переходов, созданный на стеке **Python 3.12 + FastAPI + PostgreSQL + SQLAlchemy + Alembic + Docker Compose**.

---

## 🚀 Быстрый старт (Запуск через Docker)

### 1. Предварительные требования
- Установлен и запущен **Docker Desktop**.

### 2. Запуск контейнеров
В корневой папке проекта выполните команду:
```bash
docker compose up --build
```
> При первом запуске Docker соберет образ Python-приложения, запустит контейнер PostgreSQL, подождет готовности базы, автоматически применит миграции Alembic и поднимет FastAPI на порту `8000`.

### 3. Открытие интерактивной документации
После старта откройте в браузере:
- **Swagger UI (OpenAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📌 Контракты API (Эндпоинты)

### 1. Создание короткой ссылки
- **Метод**: `POST`
- **URL**: `/api/v1/links`
- **Тело запроса (JSON)**:
```json
{
  "url": "https://example.com/some/very/long/link",
  "custom_alias": "my-alias",
  "expires_at": "2026-12-31T23:59:59Z"
}
```
*Параметры `custom_alias` и `expires_at` являются опциональными.*

- **Успешный ответ (201 Created)**:
```json
{
  "code": "my-alias",
  "url": "https://example.com/some/very/long/link",
  "created_at": "2026-02-25T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "clicks": 0
}
```

---

### 2. Редирект по короткой ссылке + учет клика
- **Метод**: `GET`
- **URL**: `/{code}` *(без префикса /api)*
- **Поведение**:
  - Увеличивает счетчик переходов `clicks` на 1.
  - Возвращает HTTP `307 Temporary Redirect` с заголовком `Location: <оригинальный URL>`.
  - Если срок жизни ссылки истек (`expires_at < now`), возвращает `410 Gone`.
  - Если ссылки нет, возвращает `404 Not Found`.

---

### 3. Получение статистики по ссылке
- **Метод**: `GET`
- **URL**: `/api/v1/links/{code}`
- **Успешный ответ (200 OK)**:
```json
{
  "code": "aZ91kL",
  "url": "https://example.com/some/very/long/link",
  "created_at": "2026-02-19T16:41:00Z",
  "expires_at": null,
  "clicks": 42
}
```

---

### 4. Список ссылок (Админ-просмотр с пагинацией)
- **Метод**: `GET`
- **URL**: `/api/v1/links?limit=50&offset=0`
- **Query-параметры**:
  - `limit`: максимальное количество ссылок (от 1 до 100, по умолчанию 50).
  - `offset`: смещение от начала списка (по умолчанию 0).
- **Успешный ответ (200 OK)**:
```json
[
  {
    "code": "promo2026",
    "url": "https://myshop.com/sale",
    "created_at": "2026-02-25T10:00:00Z",
    "expires_at": null,
    "clicks": 15
  }
]
```

---

### 5. Удаление ссылки
- **Метод**: `DELETE`
- **URL**: `/api/v1/links/{code}`
- **Успешный ответ (200 OK)**:
```json
{
  "detail": "Ссылка с кодом 'promo2026' успешно удалена."
}
```

---

## 📂 Структура проекта

```
url-shortener/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py   # Эндпоинты API v1 для работы со ссылками
│   ├── __init__.py
│   ├── config.py          # Настройки приложения через pydantic-settings
│   ├── crud.py            # Логика работы с БД (создание, чтение, удаление, клики)
│   ├── database.py        # Настройка асинхронного подключения SQLAlchemy и сессий
│   ├── models.py          # Описание таблицы 'links' в базе данных (ORM)
│   ├── schemas.py         # Pydantic-схемы валидации запросов и ответов
│   ├── utils.py           # Генератор Base62 коротких кодов
│   └── main.py            # Точка входа FastAPI, редиректы и lifecycle
├── alembic/               # Скрипты управления миграциями базы данных
│   ├── versions/          # Файлы версий схемы БД
│   └── env.py
├── alembic.ini            # Конфиг Alembic
├── Dockerfile             # Инструкция сборки контейнера с FastAPI
├── docker-compose.yml     # Сборка и связка сервиса и PostgreSQL
├── requirements.txt       # Зависимости проекта
├── .env.example           # Пример переменных окружения
└── .env                   # Переменные окружения для локальной работы
```

---

## 🛠️ Полезные команды

- **Остановка контейнеров**:
  ```bash
  docker compose down
  ```
- **Остановка с очисткой данных БД (volumes)**:
  ```bash
  docker compose down -v
  ```
- **Просмотр логов в реальном времени**:
  ```bash
  docker compose logs -f web
  ```
- **Создание новой миграции Alembic (при изменении models.py)**:
  ```bash
  docker compose exec web alembic revision --autogenerate -m "описание_изменений"
  ```
