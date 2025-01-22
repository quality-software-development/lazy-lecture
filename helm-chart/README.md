# Lazy-Lecture Helm Chart

В этом репозитории представлен Helm chart, который автоматически настраивает все компоненты для кластера Kubernetes для
сервиса перевода аудиозаписей лекций в текст "Lazy lecture".

## Содержание

- [Структура](#структура)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Сервисы](#сервисы)

---

## Структура

```
lazy-lecture/
├── Chart.yaml                  # Метаинформация о чартe
├── values.yaml                 # Настройки для всех сервисов
├── templates/                   # Шаблоны для Kubernetes объектов
│   ├── api-deployment.yaml     # Деплоймент для API сервиса
│   ├── api-service.yaml        # Сервис для API
│   ├── bot-deployment.yaml     # Деплоймент для Bot
│   ├── bot-service.yaml        # Сервис для Bot
│   ├── configmap-api-env.yaml  # Конфигурация для API
│   ├── configmap-rabbitmq.conf.yaml # Конфигурация RabbitMQ
│   ├── ingress.yaml            # Конфигурация Ingress
│   ├── postgres-deployment.yaml # Деплоймент для Postgres
│   ├── postgres-service.yaml    # Сервис для Postgres
│   ├── pvc-*.yaml              # PersistentVolumeClaim для различных сервисов
│   ├── rabbitmq-deployment.yaml # Деплоймент для RabbitMQ
│   ├── rabbitmq-service.yaml    # Сервис для RabbitMQ
│   ├── secret-postgres.yaml     # Секреты для Postgres
│   ├── secret-rabbitmq.yaml     # Секреты для RabbitMQ
│   ├── web-ui-deployment.yaml  # Деплоймент для Web-UI
│   ├── web-ui-service.yaml     # Сервис для Web-UI
│   ├── worker-deployment.yaml  # Деплоймент для Worker
└── values.yaml                 # Основные настройки
```

---

## Установка

### 1. Добавьте репозиторий Helm

Для начала необходимо добавить репозиторий Helm (если у вас его нет):

```bash
helm repo add my-repo https://github.com/nanatic/lazy-lecture-chart
helm repo update
helm install lazy-lecture my-repo/lazy-lecture
```

### 2. Установка чарта

Используйте Helm для установки чарта с настройками по умолчанию:

```bash
helm install lazy-lecture ./lazy-lecture
```

### 3. Обновление чарта

Если вам нужно обновить релиз, используйте команду:

```bash
helm upgrade lazy-lecture ./lazy-lecture
```

### 4. Удаление чарта

Для удаления релиза выполните:

```bash
helm uninstall lazy-lecture
```

---

## Конфигурация

Конфигурация вашего приложения задается через файл **`values.yaml`**. Вот основные параметры конфигурации, которые вы
можете настроить:

### **Общие настройки**

```yaml
image:
   repository: harbor.remystorage.ru/lazy-lecture
   pullPolicy: IfNotPresent
   tag: "latest"
```

Устанавливает настройки для базового образа, который используется в сервисах.

### **Сервисы**

1. **Bot**: Управляет сервисом, отвечающим за ботов.
   ```yaml
   bot:
     enabled: true
     replicaCount: 1
     image:
       repository: harbor.remystorage.ru/lazy-lecture/bot
       tag: "latest"
     env:
       BOT_TOKEN: "your-bot-token"
   ```

2. **Worker**: Этот сервис обрабатывает задачи в фоне.
   ```yaml
   worker:
     enabled: true
     replicaCount: 1
     image:
       repository: harbor.remystorage.ru/lazy-lecture/worker
       tag: "latest"
     env:
       DEVICE: "cpu"
       WHISPER_MODEL_NAME: "base"
       PIKA_HOST: "rabbitmq"
       PIKA_PORT: "5672"
       PIKA_USER: "user"
       PIKA_PASS: "pass"
   ```

3. **RabbitMQ**: Сервис для управления очередями сообщений.
   ```yaml
   rabbitmq:
     enabled: true
     replicaCount: 1
     image:
       repository: rabbitmq
       tag: "4.0.3-management"
     env:
       RMQ_USER: "user"
       RMQ_PASS: "pass"
   ```

4. **Web UI**: Веб-интерфейс для управления.
   ```yaml
   webUI:
     enabled: true
     replicaCount: 1
     image:
       repository: harbor.remystorage.ru/lazy-lecture/web-ui
       tag: "latest"
     ingress:
       enabled: true
       host: "lazy.remysorate.ru"
       tls: true
   ```

5. **API**: API для взаимодействия с платформой.
   ```yaml
   api:
     enabled: true
     replicaCount: 1
     image:
       repository: harbor.remystorage.ru/lazy-lecture/api
       tag: "latest"
     envFrom:
       - configMapRef:
           name: api-env
   ```

6. **Postgres**: Сервис для хранения данных.
   ```yaml
   postgres:
     enabled: true
     replicaCount: 1
     image:
       repository: postgres
       tag: "17.2"
     env:
       POSTGRES_DB: "lazy-lecture"
       POSTGRES_USER: "postgres"
       POSTGRES_PASSWORD: "postgres"
   ```

---

## Сервисы

Этот Helm chart включает следующие сервисы:

- **Bot** — Чат-бот для взаимодействия с пользователями.
- **Worker** — Рабочий сервис для обработки задач.
- **RabbitMQ** — Очередь сообщений для взаимодействия между сервисами.
- **Web UI** — Веб-интерфейс для пользователей.
- **API** — API для внешних приложений.
- **Postgres** — Система управления базами данных.

### Настройки сервисов:

Каждый сервис может быть включен или отключен через **`enabled`** в файле **`values.yaml`**. Также для каждого сервиса
можно настроить количество реплик (**`replicaCount`**) и параметры окружения (**`env`**).
