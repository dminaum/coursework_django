# Mailing Service (Django coursework)

Проект учебного сервиса массовых рассылок на Django: клиенты, сообщения, рассылки, попытки отправки, статистика, аутентификация.

## Стек

- Python 3.12+
- Django 5.2
- PostgreSQL 15+
- Redis
- python-dotenv
- Pillow

## Быстрый старт (локально)

1) Клонируйте репозиторий и перейдите в каталог проекта.

```bash
git clone <url> django_coursework
cd django_coursework
```

2) Создайте и активируйте виртуальное окружение, установите зависимости:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt  # если используете pip
# или через Poetry:
# pip install poetry
# poetry install
```

3) Создайте файл `.env` (можно на основе `.env.template`) и заполните переменные окружения:

```bash
cp .env.template .env
```

Обязательные переменные:

- `SECRET_KEY` — секретный ключ Django.
- `DEBUG` — `True/False`.
- База данных: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Почта: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (пароль приложения).
- **Redis:** `REDIS_URL` — адрес Redis, например:  
  `redis://localhost:6379/1`

Пример `.env`:

```bash
SECRET_KEY=dev-secret
DEBUG=True
DB_NAME=mailings
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=example@yandex.ru
EMAIL_HOST_PASSWORD=app-password
REDIS_URL=redis://localhost:6379/1
```

4) Примените миграции и создайте суперпользователя:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5) Запустите сервер разработки:

```bash
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

## Настройка Redis в Django

В `config/settings.py` замените «заглушку» на использование переменной окружения:

```python
# config/settings.py (фрагмент)
import os

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    }
}
```

И обновите `.env` как показано выше.

## Приложения и сущности

- **users** — регистрация по email, вход, профиль.
- **mailings** — клиенты, сообщения, рассылки, попытки, статистика.

Ключевые модели:
- `users.CustomUser` — пользователь с email-логином.
- `mailings.Client` — клиент (email, ФИО, комментарий, владелец).
- `mailings.Message` — текст письма (тема и тело, владелец).
- `mailings.Mailing` — рассылка (получатели, сообщение, статусы, владелец).
- `mailings.Attempt` — попытка отправки (дата, статус, ответ сервера).

## Отправка рассылок

Мгновенная отправка через кнопку в интерфейсе или через management-команду:

```bash
python manage.py send_mailing <mailing_id>
```

Команда использует `mailings.services.send_mailing_now`, который пишет записи в `Attempt` и считает статистику.

## Роли и права

Команда для инициализации группы «Менеджеры» и прав просмотра:

```bash
python manage.py bootstrap_managers
```

## Кэширование

- Главная и статистика кэшируются через Redis.
- Управляется декораторами `cache_page`, `cache_control`, `vary_on_cookie`.

## Лицензия

Skypro, курсач, август 2025