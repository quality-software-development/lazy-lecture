# Lazy Lecture

Сервис для перевода аудиозаписей лекций в текст

## Ссылки

Бот в Телеграме - [@LazyLectureBot](https://t.me/LazyLectureBot)

## Запуск проекта
### 1. Подготовка `.env` файлов
  - Создать файл `.env` в корне проекта, где указать необходимые переменные окружения. Файл имеет следующий формат

```env
RMQ_USER=user
RMQ_PASS=pass

PGADMIN_DEFAULT_EMAIL=admin@ll.ru
PGADMIN_DEFAULT_PASSWORD="asdfghjk!@#$%^&*"
PGADMIN_CONFIG_SERVER_MODE=False

BOT_TOKEN="СЮДА_ВСТАВЛЯЕТЕ_ТОКЕН"
SECRET_WORKER_TOKEN="q8yn12312c1r98y702"

```
  - Создать файл ` api/config/.env`:
<details>
<summary>Посмотреть пример `api/config/.env`</summary>
  
```env
# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Kartoshe4ku?
ADMIN_EMAIL=admin@admin.admin

# JWT Token
SECRET_KEY=s3cr3t_k3y
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Database Healthcheck
PGUSER=$POSTGRES_USER
PGDATABASE=$POSTGRES_DB

# Object storage path
OBJECT_STORAGE_PATH=/object_storage

# Task queue connection
PIKA_HOST=rabbitmq
PIKA_PORT=5672
PIKA_USER=user
PIKA_PASS=pass
PIKA_QUEUE=task_queue
```
</details>

  - В продакшене поменять пароли!

### 2. Поднять сервисы с помощью Docker Compose:

```shell
docker compose --env-file .env up -d
```

Или если требуется запустить отдельный сервис:

```shell
docker compose --env-file .env up <service_name>
```
**Пример:**
```shell
docker compose --env-file .env up --build api worker bot
```
```shell
docker compose --env-file .env down api worker bot
```
## pre-commit

Для CI в репозитории используется pre-commit хук. Перед коммитом, пожалуйста, прогоните его.

```shell
pip install pre-commit
pre-commit install
pre-commit run
```

По умолчанию, pre-commit работает только для файлов на стадии "staged" в git. Чтобы запустить
pre-commit для всех файлов (и сразу отформатировать их под требования pre-commit хуков),
можно использовать следующую команду:

```shell
pre-commit run --all-files
```
