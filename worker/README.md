# Lazy Lecture Worker

Ядро системы обработки аудиозаписи

Используем для транскрипции [Whisper](https://github.com/openai/whisper) от OpenAI

## Запуск

Понадобится Docker.

- В директории проекта выполнить:

```bsah
$ docker-compose up -d worker
```

## Запуск модульных тестов с Coverage

```bash
docker compose run -it --build worker python -m pytest tests/unit --cov=. --cov-report term-missing
```

## Параметры

```env
DEVICE=auto
MODEL_NAME=tiny
DOWNLOAD_ROOT=/cache
PIKA_HOST=localhost
PIKA_PORT=5672
PIKA_USER=rmuser
PIKA_PASS=rmpassword
PIKA_QUEUE=task_queue
```
