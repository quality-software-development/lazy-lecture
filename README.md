# Lazy Lecture

Сервис для перевода аудиозаписей лекций в текст

## Ссылки

Бот в Телеграме - [@LazyLectureBot](https://t.me/LazyLectureBot)

## Запуск проекта

1. Создать файл `.env` в корне проекта, где указать необходимые переменные окружения. Файл имеет следующий формат

```env
BOT_TOKEN=<your_bot_token_here>
```


Прописать в `api/config/.env` нормальный пароль `ADMIN_PASSWORD=`. Иначе Pydantic накричит на вас и API откажется работать 
```env
ADMIN_PASSWORD=Kartoshe4ku?
```

Добавить в корень проекта `.env`
```env
SECRET_WORKER_TOKEN=somestring
```


1. Поднять сервисы с помощью Docker Compose:

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

По умолчанию, pre-commit работает только для файлов на стадии "staged" в git. Чтобы запустить
pre-commit для всех файлов (и сразу отформатировать их под требования pre-commit хуков),
можно использовать следующую команду:

```bash
pre-commit run --all-files
```
