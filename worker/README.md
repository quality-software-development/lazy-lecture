# Lazy Lecture Worker

Ядро системы обработки аудиозаписи

Используем для транскрипции [Wisper](https://github.com/openai/whisper) от OpenAI
## Запуск

Понадобится Docker.

- В директории проекта выполнить:

```bsah
$ docker-compose up -d worker
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
