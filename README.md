# PlantCare Backend

Backend-часть информационной системы PlantCare. Система позволяет пользователю загрузить фотографию растения, распознать его вид, получить структурированные рекомендации по уходу, добавить растение в персональную галерею и отслеживать события полива.

Backend реализован на FastAPI и предназначен для совместной работы с Android-клиентом и React-сайтом.

## Основной функционал

- регистрация пользователей;
- авторизация через JWT;
- получение и редактирование профиля пользователя;
- загрузка аватара пользователя;
- загрузка фотографии растения;
- сохранение фотографии растения на backend;
- распознавание растения через PlantNet API;
- генерация рекомендаций по уходу через OpenRouter API;
- fallback-рекомендации при недоступности AI-сервиса;
- добавление растения в персональную галерею пользователя;
- просмотр, редактирование и удаление растений из галереи;
- автоматическая генерация событий полива;
- просмотр событий полива;
- отметка полива как выполненного;
- пропуск события полива.

## Технологический стек

- Python 3.13+
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT / python-jose
- Passlib / bcrypt
- httpx
- OpenAI SDK
- PlantNet API
- OpenRouter API
- Pytest

## Структура проекта

```text
app/
├── api/
│   ├── api.py
│   └── v1/
│       ├── deps.py
│       └── endpoints/
│           ├── auth.py
│           ├── users.py
│           ├── plants.py
│           ├── gallery.py
│           └── care.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/
│   ├── user.py
│   ├── plant.py
│   ├── user_plant.py
│   └── watering_event.py
├── schemas/
│   ├── user.py
│   ├── token.py
│   ├── plant.py
│   ├── gallery.py
│   └── watering.py
├── services/
│   ├── user_service.py
│   ├── plant_service.py
│   ├── plantnet_service.py
│   ├── deepseek_service.py
│   ├── gallery_service.py
│   └── care_service.py
└── main.py
```

## Логика работы

```text
Пользователь загружает фото растения
        ↓
Backend сохраняет фото растения
        ↓
Backend отправляет фото в PlantNet API
        ↓
PlantNet возвращает предполагаемый вид растения
        ↓
Backend отправляет название растения в OpenRouter API
        ↓
OpenRouter возвращает структурированный JSON с рекомендациями
        ↓
Backend сохраняет растение в таблицу plants
        ↓
Backend возвращает plant_id и image_url
        ↓
Пользователь подтверждает растение
        ↓
Клиент отправляет plant_id и image_url в /gallery
        ↓
Backend добавляет растение в галерею пользователя
        ↓
Backend автоматически создает события полива
```


## Основные сущности

### User

Пользователь системы.

Поля:

- `id`
- `email`
- `username`
- `hashed_password`
- `avatar_url`
- `created_at`
- `updated_at`

### Plant

Справочная карточка растения.

Поля:

- `id`
- `common_name`
- `scientific_name`
- `description`
- `watering_info`
- `watering_interval_days`
- `light_info`
- `min_temperature_celsius`
- `max_temperature_celsius`
- `humidity_info`
- `soil_info`
- `fertilizing_info`
- `fertilizing_interval_days`
- `care_info`
- `useful_info`
- `created_at`

### UserPlant

Растение в персональной галерее пользователя.

Поля:

- `id`
- `user_id`
- `plant_id`
- `custom_name`
- `image_url`
- `last_watered_at`
- `next_watering_date`
- `added_at`

### WateringEvent

Событие полива.

Поля:

- `id`
- `user_plant_id`
- `scheduled_date`
- `completed_at`
- `status`
- `note`
- `created_at`

Возможные статусы:

```text
planned
completed
skipped
```

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd backend
```

### 2. Создать виртуальное окружение

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```


### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

В корне backend-проекта создать файл `.env`.

```env
APP_NAME=PlantCare
APP_VERSION=1.0.0
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/plantcare_db

SECRET_KEY=super_secret_key_for_dev
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

PLANTNET_API_KEY=your_plantnet_api_key
PLANTNET_API_URL=https://my-api.plantnet.org/v2/identify/all

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-v4-flash:free
```

### 5. Создать базу данных PostgreSQL

```sql
CREATE DATABASE plantcare_db;
```

### 6. Запустить сервер

```bash
uvicorn app.main:app --reload
```

API будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger-документация:

```text
http://127.0.0.1:8000/docs
```

## Статические файлы

Backend сохраняет пользовательские изображения в директорию:

```text
static/uploads/
```

Используются подкаталоги:

```text
static/uploads/avatars/
static/uploads/plants/
```

Пример URL изображения:

```text
/static/uploads/plants/plant_1_abcd1234.jpg
```

Для доступа из клиента полный URL формируется так:

```text
http://127.0.0.1:8000/static/uploads/plants/plant_1_abcd1234.jpg
```

## API endpoints

### Health check

```http
GET /api/v1/health
```

### Auth

#### Регистрация

```http
POST /api/v1/auth/register
```

Тело запроса:

```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "123456"
}
```

#### Авторизация

```http
POST /api/v1/auth/login
```

Тело запроса:

```json
{
  "email": "user@example.com",
  "password": "123456"
}
```

Ответ:

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### Users

```http
GET /api/v1/users/me
PATCH /api/v1/users/me
POST /api/v1/users/me/avatar
```

`POST /users/me/avatar` принимает `multipart/form-data` с полем `file`. Поддерживаемые форматы: JPG, PNG, WEBP.

### Plants

```http
POST /api/v1/plants/mock-recognize
POST /api/v1/plants/recognize
```

`POST /plants/recognize` принимает `multipart/form-data` с полем `file`.

Пример ответа:

```json
{
  "plant_id": 1,
  "common_name": "Монстера",
  "scientific_name": "Monstera deliciosa",
  "description": "Популярное комнатное растение с крупными декоративными листьями.",
  "watering_info": "Поливать после подсыхания верхнего слоя почвы.",
  "watering_interval_days": 7,
  "light_info": "Предпочитает яркий рассеянный свет.",
  "min_temperature_celsius": 18.0,
  "max_temperature_celsius": 26.0,
  "humidity_info": "Предпочитает умеренную влажность воздуха.",
  "soil_info": "Подходит рыхлый грунт с хорошим дренажем.",
  "fertilizing_info": "Подкармливать в период активного роста один раз в месяц.",
  "fertilizing_interval_days": 30,
  "care_info": "Избегать переувлажнения и резких перепадов температуры.",
  "useful_info": "Перед добавлением растения рекомендуется проверить результат распознавания.",
  "confidence": 0.92,
  "image_url": "/static/uploads/plants/plant_1_abcd1234.jpg"
}
```

### Gallery

```http
GET    /api/v1/gallery
GET    /api/v1/gallery/{user_plant_id}
POST   /api/v1/gallery
PATCH  /api/v1/gallery/{user_plant_id}
DELETE /api/v1/gallery/{user_plant_id}
```

Пример добавления растения:

```json
{
  "plant_id": 1,
  "custom_name": "Моя монстера",
  "image_url": "/static/uploads/plants/plant_1_abcd1234.jpg"
}
```

После добавления backend автоматически создает события полива.

### Care

```http
GET   /api/v1/care/watering-events
GET   /api/v1/care/watering-events/today
GET   /api/v1/care/user-plants/{user_plant_id}/watering-events
PATCH /api/v1/care/watering-events/{event_id}/complete
PATCH /api/v1/care/watering-events/{event_id}/skip
```

Фильтр по статусу:

```http
GET /api/v1/care/watering-events?status=planned
```

Пример выполнения полива:

```json
{
  "note": "Полив выполнен утром"
}
```

После выполнения backend:

- меняет статус события на `completed`;
- записывает `completed_at`;
- обновляет `last_watered_at`;
- обновляет `next_watering_date`;
- создает следующее событие полива, если его еще нет.

## Авторизация

Для защищенных endpoint'ов используется JWT.

```http
Authorization: Bearer <access_token>
```



## Статус проекта

Backend реализует MVP системы PlantCare:

```text
профиль пользователя
    → загрузка аватара
    → загрузка фото растения
    → распознавание через PlantNet
    → рекомендации через OpenRouter или fallback
    → сохранение фото на backend
    → добавление растения в галерею
    → автоматические события полива
```

Проект готов для интеграции с Android-клиентом и React-сайтом.
