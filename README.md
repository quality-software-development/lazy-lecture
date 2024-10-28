# Lazy Lecture

Сервис для перевода аудиозаписей лекций в текст

## Ссылки

Бот в Телеграме - [@LazyLectureBot](https://t.me/LazyLectureBot)

## Запуск проекта

1. Создать файл `.env` в корне проекта, где указать необходимые переменные окружения. Файл имеет следующий формат

```env
BOT_TOKEN=<your_bot_token_here>
```

2. Поднять сервисы с помощью Docker Compose:

```bash
docker compose --env-file .env up -d
```

Или если требуется запустить отдельный сервис:

```bash
docker compose --env-file .env up <service_name>
```

## pre-commit

Для CI в репозитории используется pre-commit хук. Перед коммитом, пожалуйста, прогоните его.

```bash
pip install pre-commit
pre-commit install
pre-commit run
```
