# Отчёт по интеграционному тестированию

**Проект:** Lazy Lecture — сервис расшифровки лекций (audio → text)

**Дата:** -

**Команда:** quality-software-development

n> Документ продолжает курсовую работу №2 по дисциплине «Технологии разработки качественного программного обеспечения».

---

## 0. Введение

**Цель документа:** предоставить исчерпывающее описание интеграционных тестов для проекта Lazy Lecture, включающее перечень тестовых сценариев, используемые инструменты и техники, план выполнения и порядок дальнейшего расширения набора. Документ предназначен для согласования у преподавателя и/или владельца продукта и для последующей сверки в код-ревью.

**Область применения:** интеграционное тестирование охватывает проверку взаимодействия между ключевыми модулями и внешними подсистемами проекта:
- сервис `api` (FastAPI) ↔ Pydantic-схемы ↔ SQLAlchemy ORM ↔ PostgreSQL,
- `api` ↔ файловое хранилище (`aiofiles`) ↔ ffmpeg,
- `api` ↔ очередь задач RabbitMQ.

В качестве заменителя реальной БД и очереди используются мок-объекты, изолирующие тестовую среду от внешних ресурсов.

---

## План выполнения интеграционных тестов

1. **Подготовка тестовой среды.** Формирование окружения с использованием mock-объектов (`AsyncMock`, `MagicMock`, `monkeypatch`); настройка CI-сервера (GitHub Actions); фиксация версий зависимостей в `api/config/requirements.txt`.
2. **Разработка тестовых сценариев.** Создание описания тест-кейсов (см. раздел 2 ниже): SUT, downstream-зависимости, состояние «до» и «после», ожидаемое поведение для позитивного и негативного случая. Согласование сценариев у преподавателя.
3. **Запуск и мониторинг тестов.** Автоматический запуск тестов по событию `push` / `pull_request` или по расписанию. Сбор логов и первичный анализ результатов в Sonar.
4. **Отчётность.** Формирование отчёта о прохождении (раздел 3) — заполняется после каждого прогона.

---

## 1. Описание выполненной работы

### 1.1 Объект тестирования

Интеграционные тесты проверяют взаимодействие нескольких слоёв одного сервиса между собой и с моками внешних подсистем. Покрываются ключевые цепочки api-сервиса:

- **Аутентификация** — `authenticate_user` поверх `User`-модели и (мокированной) сессии `AsyncSession`.
- **Регистрация** — `create_user` через `UserCreate`-схему: валидация → хеширование → запись.
- **Загрузка аудио** — `create_upload_file`: валидация прав пользователя, проверка отсутствия активных задач, запись на диск (`aiofiles`), создание записи в БД, отправка задания в очередь.
- **Список транскрипций** — `list_user_transcriptions`: формирование пагинированного ответа, обогащение полем `description`.
- **Статус транскрипции** — `info_transcript`: чтение по ID с проверкой владельца.

### 1.2 Используемые инструменты

| Инструмент | Назначение |
|------------|-----------|
| `pytest` 8.3 + `pytest-asyncio` | Async-тесты |
| `unittest.mock` (`AsyncMock`, `MagicMock`, `monkeypatch`) | Подмена SQLAlchemy сессии, файлового ввода-вывода, очереди RabbitMQ |
| `fastapi.testclient.TestClient` | (для `conftest.py`) поднятие FastAPI приложения внутри теста |
| `aiosqlite` (in-memory) | Резервная БД для тестов, требующих реального движка |
| GitHub Actions | CI: запускает `pytest tests/integration_tests` после `pytest tests/unit_tests` |

### 1.3 Применение заглушек (mock)

**Реальные компоненты:**
- Pydantic-схемы и валидаторы (`UserCreate`, `Credentials`, `Transcription`).
- Доменные сервисы (`authenticate_user`, `create_user`, `list_user_transcriptions`, `info_transcript`, `create_upload_file`).
- Хеширование паролей (`get_password_hash` / `verify_password`, реальный bcrypt).
- ORM-модели `User`, `Transcription`, enum `TranscriptionState`.

**Мокированные компоненты:**
- `AsyncSession` (sqlalchemy) — `AsyncMock` со скриптом `scalar` / `scalars` / `get_one` / `add` / `commit` / `refresh`.
- Файловое хранилище — `aiofiles.open` подменяется на `DummyAiofilesContextManager`.
- `os.path.join` — фиксированный путь для предсказуемости.
- `RabbitMQ`-канал — `MagicMock` с `basic_publish`.
- Получение длительности аудио (`ffmpeg-python`) — лямбда, возвращающая 120.0 сек.
- Внутренние функции (через `monkeypatch.setattr`): `verify_password`, `get_current_transcriptions`, `create_transcription`, `get_transcritption_descrtiption`.

### 1.4 Классификация тестов

#### По уровню изоляции

Интеграционные тесты Lazy Lecture обеспечивают **частичную изоляцию**: связка «view → service → schema → ORM-модель» работает целиком, заменяются только I/O-границы (БД, файловая система, очередь, ffmpeg). Если тест падает — проблема во взаимодействии слоёв.

| Компонент | Состояние |
|-----------|-----------|
| Сервисный слой | реальный |
| Pydantic-схемы | реальные |
| ORM-модели (как Python-классы, без БД-движка) | реальные |
| `AsyncSession` SQLAlchemy | замокирован |
| Файловое хранилище | замокировано |
| RabbitMQ | замокировано |
| ffmpeg | замокирован |

#### По подходу к тестированию

| Подход | Описание | Применение |
|--------|----------|------------|
| **Серый ящик** (gray-box) | Тестировщик знает структуру: подменяет внутренние функции через `monkeypatch`, проверяет вызовы моков и возвращаемые значения | Все 5 сценариев интеграции |

#### По назначению теста

| Назначение | Маркер | Кол-во | Описание |
|------------|--------|--------|----------|
| Штатный сценарий | EC | 5 | Все позитивные пути: вход, регистрация, загрузка, список, статус |
| Путь ошибки | EP | 0 | (Покрываются на уровне unit-тестов соответствующих сервисов) |

#### По объекту тестирования

| Категория | Файл | Тестов | Объект |
|-----------|------|--------|--------|
| Аутентификация | `api/tests/integration_tests/test_integration_api.py` | 1 | `authenticate_user` + ORM `User` + `verify_password` |
| Регистрация | `api/tests/integration_tests/test_integration_api.py` | 1 | `create_user` + `UserCreate` + хеширование + `db.add/commit/refresh` |
| Загрузка аудио | `api/tests/integration_tests/test_integration_api.py` | 1 | `create_upload_file` + `aiofiles` + `get_audio_duration` + RabbitMQ + `create_transcription` |
| Список транскрипций | `api/tests/integration_tests/test_integration_api.py` | 1 | `list_user_transcriptions` + `Transcription` + пагинация + `get_transcritption_descrtiption` |
| Статус транскрипции | `api/tests/integration_tests/test_integration_api.py` | 1 | `info_transcript` + `Transcription` + проверка владельца |
| **ИТОГО** | **1 файл** | **5** | |

### 1.5 Применённые техники тест-дизайна

**КЭ (классы эквивалентности).** Каждый тест представляет позитивный класс «всё хорошо» по своей цепочке:
- `test_authorization_user`: класс «пользователь существует, активен, пароль корректен».
- `test_registration_user`: класс «новый username, пароль валиден».
- `test_upload_audio`: класс «can_interact = True, нет активных задач, audio/mpeg, длительность валидна».
- `test_list_user_transcriptions`: класс «у пользователя есть ≥1 транскрипция, описание формируется».
- `test_get_transcription_status`: класс «транскрипция принадлежит пользователю, состояние in_progress».

**ПП (попарное).** В `test_upload_audio` одновременно проверяется взаимодействие пяти подсистем (валидация прав × хранилище × длительность × БД × очередь): успешный путь требует, чтобы все моки сложились.

**Decision Table.** В сценарии загрузки аудио неявно задаётся таблица решений: `(can_interact, current_transcriptions_empty, content_type, длительность) → upload OK`. Текущий набор покрывает только клетку «всё true», прочие клетки — на уровне unit-тестов в `tests/unit_tests/transcriptions/`.

### 1.6 Непрерывная интеграция

```
api unit (pytest tests/unit_tests) → api integration (pytest tests/integration_tests) → bot/worker/web-ui unit
```

В CI используется тот же `pytest` без флага `-race` (Python). Каждый тест получает свежий `AsyncMock`, побочных эффектов между тестами нет.

---

## 2. Тест-план

### 2.1 Перечень сценариев

| № | Сценарий | Тип | Слои |
|---|----------|-----|------|
| 1 | Валидные admin-учётные данные → объект `User` | Позитивный | `authenticate_user` + `User` + `verify_password` |
| 2 | Регистрация нового пользователя → объект `User` с хешированным паролем и `id` | Позитивный | `create_user` + `UserCreate` + bcrypt + `db.add/commit/refresh` |
| 3 | Загрузка валидного аудио → создаётся транскрипция, файл сохранён, задание в очереди | Позитивный | `create_upload_file` + `aiofiles` + `ffmpeg` + `Transcription` + RabbitMQ |
| 4 | Запрос списка транскрипций пользователя → пагинированный ответ с описанием | Позитивный | `list_user_transcriptions` + пагинация |
| 5 | Запрос статуса своей транскрипции → объект с `id` и `current_state` | Позитивный | `info_transcript` + `Transcription` |

### 2.2 Описание сценариев

Для каждого сценария указаны **SUT** (System Under Test) и **Downstream** (зависимости, заменённые моками или реальные), а также **состояние «до»** и **состояние «после»** для позитивного и негативного случая.

---

#### 2.2.1 Авторизация пользователя

- **SUT:** `source.app.auth.services.authenticate_user`
- **Downstream:** SQLAlchemy `AsyncSession` (БД пользователей), `verify_password` (bcrypt).
- **Детальный сценарий:** функция получает `username` и `password`, обращается к БД за хэшем и валидирует пароль. Если пользователь найден, активен и хэш совпадает — возвращается `User`; иначе — `None` либо исключение.

**Сценарий 1 (успешный):**
- *Состояние до:* запись пользователя существует в БД, `active=True`, пароль корректен.
- *Состояние после:* возвращён объект `User` с тем же `id` и полями из БД.

**Сценарий 2 (неуспешный — неверный пароль):**
- *Состояние до:* пользователь найден и активен, но передан неверный пароль.
- *Состояние после:* возвращается `None`.

**Сценарий 3 (неуспешный — неактивный пользователь):**
- *Состояние до:* пользователь найден, но `active=False`.
- *Состояние после:* выбрасывается `HTTPException("Your account is blocked")`.

**Тест-представитель (Listing):**

```python
async def test_authorization_user(monkeypatch):
    fake_user = User()
    fake_user.id = 1
    fake_user.username = "testuser"
    fake_user.password = "hashedpassword"
    fake_user.active = True
    fake_user.password_timestamp = 1234567890.0

    fake_db = AsyncMock()
    fake_db.scalar = AsyncMock(return_value=fake_user)

    monkeypatch.setattr("source.app.auth.services.verify_password",
                        lambda plain_password, hashed_password: True)

    result = await authenticate_user("testuser", "TestP@ss123", fake_db)
    assert result is fake_user
```

---

#### 2.2.2 Регистрация пользователя

- **SUT:** `source.app.users.services.create_user`
- **Downstream:** `AsyncSession` (БД пользователей), bcrypt.
- **Детальный сценарий:** функция принимает `UserCreate`, хеширует пароль, создаёт запись пользователя в БД, коммитит и обновляет объект (присваивает `id`). При `IntegrityError` (дубликат `username`) возвращает `None`.

**Сценарий 1 (успешный):**
- *Состояние до:* в БД нет пользователя с таким `username`.
- *Состояние после:* создан новый пользователь с `id=1`, пароль сохранён в хэше (≠ исходного).

**Сценарий 2 (неуспешный — дубликат):**
- *Состояние до:* в БД уже есть пользователь с тем же `username`.
- *Состояние после:* `db.commit()` бросает `IntegrityError`, функция возвращает `None`.

**Тест-представитель:**

```python
async def test_registration_user(monkeypatch):
    user_data = UserCreate(username="newuser", password="ValidP@ss123")
    fake_db = AsyncMock()
    fake_db.add = MagicMock()
    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock(side_effect=lambda user: setattr(user, "id", 1) or None)

    result = await create_user(user_data, fake_db)
    assert result is not None
    assert result.username == "newuser"
    assert result.password != "ValidP@ss123"   # хешировано
    assert hasattr(result, "id") and result.id == 1
```

---

#### 2.2.3 Загрузка аудио для обработки

- **SUT:** `source.app.transcriptions.views.create_upload_file`
- **Downstream:** файловое хранилище (`aiofiles`), Queue Service (RabbitMQ-канал), Transcriptions Service (`create_transcription`, `get_current_transcriptions`), `ffmpeg` (`get_audio_duration`).
- **Детальный сценарий:** принимается `User` и файл; проверяется `can_interact`; читаются чанки через `aiofiles`, сохраняются на диск; вычисляется длительность аудио; создаётся запись транскрипции; в очередь отправляется задача.

**Сценарий 1 (успешный):**
- *Состояние до:* в хранилище нет конфликтующих файлов; `user.can_interact = True`; очередь доступна; активных задач у пользователя нет.
- *Состояние после:* файл сохранён по пути `/dummy_path/...`; создана транскрипция `id=42`; в очередь отправлено сообщение; возвращён JSON `{"message":"File uploaded successfully","task_id":42,...}`.

**Сценарий 2 (неуспешный — пользователь не может взаимодействовать):**
- *Состояние до:* `user.can_interact = False`.
- *Состояние после:* выбрасывается `HTTPException("Access restricted")`.

**Тест-представитель:** см. `api/tests/integration_tests/test_integration_api.py::test_upload_audio` (полный код приведён в курсовой работе №2, листинг к разделу 4.3).

---

#### 2.2.4 Взятие списка транскрипций пользователя

- **SUT:** `source.app.transcriptions.services.list_user_transcriptions`
- **Downstream:** БД транскрипций, Description Provider (`get_transcritption_descrtiption`).
- **Детальный сценарий:** функция получает `page`, `size`, `user_id`; запрашивает общее число (`scalar`) и страницу (`scalars().all()`); для каждого результата дёргает получение описания; возвращает объект пагинации.

**Сценарий 1 (есть транскрипции):**
- *Состояние до:* в БД есть 1 транскрипция для пользователя `id=1`.
- *Состояние после:* возвращён объект с `total=1`, список из 1 элемента, у которого `description="dummy description"`.

**Сценарий 2 (нет транскрипций):**
- *Состояние до:* в БД нет транскрипций для `user_id`.
- *Состояние после:* `total=0`, пустой список `transcriptions`.

---

#### 2.2.5 Взятие статуса транскрипции

- **SUT:** `source.app.transcriptions.services.info_transcript`
- **Downstream:** БД транскрипций.
- **Детальный сценарий:** функция получает `user_id` и `transcript_id`, запрашивает запись, проверяет право доступа (`creator_id == user_id`), возвращает объект транскрипции с текущим `current_state`.

**Сценарий 1 (успешный):**
- *Состояние до:* запись транскрипции `id=55` существует, `creator_id=1`.
- *Состояние после:* возвращён объект, `current_state=IN_PROGRESS`.

**Сценарий 2 (неуспешный — чужая транскрипция):**
- *Состояние до:* запись существует, но `creator_id ≠ user_id`.
- *Состояние после:* выбрасывается `ValueError("You may cancel processing only of your transcript")`.

**Тест-представитель:**

```python
async def test_get_transcription_status(monkeypatch):
    dummy_transcription = Transcription()
    dummy_transcription.id = 55
    dummy_transcription.creator_id = 1
    dummy_transcription.current_state = TranscriptionState.IN_PROGRESS

    fake_db = AsyncMock()
    fake_db.get_one = AsyncMock(return_value=dummy_transcription)

    result = await info_transcript(user_id=1, transcript_id=55, db=fake_db)
    assert result.current_state == TranscriptionState.IN_PROGRESS
    assert result.id == 55
```

### 2.3 Покрытые пути взаимодействия

| Связка | Сценарий | Что проверяется на стыке |
|--------|----------|--------------------------|
| view → service | №3 | `create_upload_file` (view) корректно передаёт параметры в `create_transcription` (service) |
| service → schema | №2 | `create_user` (service) принимает `UserRequest`, конвертирует в `UserCreate`, тот применяет валидатор-хеширование |
| service → ORM | №1, 4, 5 | `authenticate_user` / `info_transcript` корректно читают атрибуты моделей |
| service → I/O | №3 | `aiofiles`, `ffmpeg`, RabbitMQ зовутся в правильном порядке |
| service → пагинация | №4 | Подсчёт `total` через `scalar` и наполнение `transcriptions` через `scalars().all()` |

---

## 3. Результаты тестирования

| Метрика | Значение |
|---------|----------|
| Всего интеграционных тестов | 5 |
| Пройдено | **5 (100%)** |
| Провалено | 0 |
| Среднее время одного теста | ~0.2 c |
| Полное время | ~1.1 c |
| Покрытие интеграционными тестами по api/source/app | ~40% (дополняет ~85% от unit-тестов) |

```
$ python -m pytest api/tests/integration_tests -v
collected 5 items

tests/integration_tests/test_integration_api.py::test_authorization_user PASSED      [ 20%]
tests/integration_tests/test_integration_api.py::test_registration_user PASSED       [ 40%]
tests/integration_tests/test_integration_api.py::test_upload_audio PASSED            [ 60%]
tests/integration_tests/test_integration_api.py::test_list_user_transcriptions PASSED[ 80%]
tests/integration_tests/test_integration_api.py::test_get_transcription_status PASSED[100%]

============================== 5 passed in 1.11s ==============================
```

### 3.1 Прогон в CI (GitHub Actions)

Общий пайплайн (упрощённо):

```text
┌──────────────────────────────┐    ┌─────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────────┐
│ Сборка и установка зависимостей │ ─▶ │ Юнит-тесты API │ ─▶ │ Интеграционные тесты API │ ─▶ │ Анализ покрытия и SonarQube │
└──────────────────────────────┘    └─────────────────┘    └──────────────────────────┘    └──────────────────────────────┘
                                            │
                                            ├─▶ Тесты worker
                                            ├─▶ Тесты bot
                                            └─▶ Тесты web-ui
```

Скриншоты пайплайна и логов прогона приведены в `docs/Курсовая_работа_ТРКПО_Интеграционки.docx.pdf` (Рис. 1 — пайплайн, Рис. 2 — выполнение тестов).

**Аналитика логов CI** позволяет проверить:
1. Корректную реакцию тестов на возникающие ошибки (нужный exit-code, понятный traceback).
2. Соответствие названий тестов запускаемым модулям и use-cases (читаемый отчёт `pytest -v`).
3. Полное выполнение всех заявленных интеграционных тестов (5/5 в текущем прогоне).

---

## 4. Команды запуска (от корня репозитория)

### 4.1 Только интеграционные тесты api

```cmd
pushd api && python -m pytest tests/integration_tests -v && popd
```

### 4.2 Unit + integration вместе

```cmd
pushd api && python -m pytest tests/unit_tests tests/integration_tests -v && popd
```

### 4.3 С покрытием

```cmd
pushd api && python -m pytest tests/integration_tests --cov=source.app --cov=source.core --cov-report=term-missing && popd
```

### 4.4 Отдельный сценарий

```cmd
pushd api && python -m pytest "tests/integration_tests/test_integration_api.py::test_upload_audio" -v -s && popd
```

> `-s` — показать `print`/логи. Полезно при отладке последовательности вызовов моков.

---

## 5. Процедура расширения интеграционного тестового набора

Процедура состоит из **пяти этапов**, обеспечивающих полное покрытие новой функциональности при сохранении стабильности существующего набора:

1. **Анализ требований.** На первом этапе изучаются требования к новой функциональной части: какие задачи решает модуль, какие входные/выходные данные использует, как взаимодействует с остальными компонентами системы (БД, очередь, файловое хранилище, внешние API).
2. **Разработка тестовых сценариев.** На основании требований формируются тест-кейсы, охватывающие как **позитивные**, так и **негативные** случаи. Особое внимание — граничным условиям и взаимодействию с внешними сервисами и БД. Каждый сценарий описывается в формате SUT / Downstream / Состояние «до» / Состояние «после» (см. раздел 2.2).
3. **Интеграция тестов.** Новые тесты добавляются в существующий тестовый фреймворк (`api/tests/integration_tests/`), регистрируются в системе сборки (`pytest`) и CI/CD (GitHub Actions). Это позволяет выполнять все тесты в рамках единого пайплайна и отслеживать влияние изменений на остальные модули.
4. **Запуск и отладка тестов.** Выполняется первый запуск новых тестов. При необходимости производится отладка, исправление ошибок как в коде тестов, так и в бизнес-логике тестируемой функциональности.
5. **Автоматизация тестов.** После верификации корректности выполнения тесты подготавливаются к автоматизированному исполнению: стабилизация окружения, настройка моков, вынесение повторно используемых заглушек в `conftest.py` для будущего использования.

### 5.1 Конкретный пример (для нового эндпоинта)

При добавлении нового функционального модуля (например, `DELETE /transcriptions/{id}` — удаление с очисткой файла из object-storage):

1. Определить участвующие слои: `view → service → DB → object-storage`.
2. Добавить функцию `test_delete_transcription` в `api/tests/integration_tests/test_integration_api.py`.
3. Замокать через `monkeypatch.setattr` зависимости, граничащие с I/O: SQLAlchemy-сессию, файловое API, очередь.
4. Заполнить позитивный класс эквивалентности (всё валидно). Для негативных случаев (нет прав, файла не существует, БД роняет `IntegrityError`) — добавить тесты в соответствующий unit-файл.
5. Убедиться, что моки вызваны в правильном порядке (`assert_called_once_with`, `call_args_list`).
6. Запустить и проверить, что покрытие view-функции — 100%, а покрытие service ≥ 80%.

**Шаблон:**

```python
@pytest.mark.asyncio
async def test_delete_transcription_success(monkeypatch, tmp_path):
    """
    Сквозной позитивный сценарий удаления:
    view вызывает service, service удаляет запись в БД и стирает файл с диска.
    """
    from source.app.transcriptions.views import delete_transcription
    from source.app.transcriptions.models import Transcription

    user = User(); user.id = 1; user.can_interact = True
    transcription = Transcription()
    transcription.id = 42
    transcription.creator_id = 1

    # БД отдаёт запись пользователя и подтверждает удаление
    fake_db = AsyncMock()
    fake_db.get_one = AsyncMock(return_value=transcription)
    fake_db.delete = AsyncMock()
    fake_db.commit = AsyncMock()

    # На диске есть файл — он должен исчезнуть
    audio_file = tmp_path / "42.mp3"
    audio_file.write_bytes(b"audio")
    monkeypatch.setattr(
        "source.app.transcriptions.views.OBJECT_STORAGE_PATH", str(tmp_path)
    )

    result = await delete_transcription(user, 42, fake_db)
    assert result["message"] == "Transcription deleted"
    assert not audio_file.exists()
    fake_db.delete.assert_awaited_once_with(transcription)
    fake_db.commit.assert_awaited_once()
```

При появлении нового сервиса (например, billing) — создать `api/tests/integration_tests/test_billing_integration.py` с собственным набором фикстур.
