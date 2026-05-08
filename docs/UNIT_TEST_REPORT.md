# Отчёт по модульному тестированию

**Проект:** Lazy Lecture — сервис расшифровки лекций (audio → text)

**Дата:** -

**Команда:** quality-software-development

> Документ продолжает линейку курсовых работ по дисциплине «Технологии разработки качественного программного обеспечения» (Курсовая №1 — модульное тестирование). Цели и задачи, перечень техник тест-дизайна и подход к расширению набора согласованы с требованиями курса.

---

## 0. Цель и задачи тестирования

**Цель:** обеспечить заданное покрытие кода модульными тестами и автоматический контроль качества при каждом изменении исходного кода.

**Задачи:**
- Достичь покрытия кода тестами **не менее 80%** для основного модуля `api` и не менее 70% — для каждого вспомогательного (`bot`, `worker`, `web-ui`).
- Обеспечить **автоматический запуск тестов** при сборке проекта (CI / pre-commit) и регистрацию результатов в SonarQube.
- Реализовать **не менее 25 тестов на модуль** с применением минимум 7 техник тест-дизайна.
- Покрыть позитивные, негативные и граничные классы входов для каждой бизнес-функции.

---

## 1. Описание выполненной работы

### 1.1 Объект тестирования

Lazy Lecture — распределённый сервис расшифровки аудиозаписей лекций. Состоит из четырёх независимо разворачиваемых сервисов, общающихся через RabbitMQ и REST:

| Сервис | Стек | Назначение | Порт |
|--------|------|-----------|------|
| `api/`     | FastAPI + SQLAlchemy + PostgreSQL | REST API: пользователи, аутентификация (JWT), жизненный цикл транскрипций | 8000 |
| `worker/`  | Python + openai-whisper + aio-pika | Потребитель задач из очереди RabbitMQ, ASR-инференс | — |
| `bot/`     | aiogram 3 (asyncio) | Telegram-бот: фронт для пользователя, проксирует к API | — |
| `web-ui/`  | Vue 3 + Quasar 2 + Pinia + TypeScript | Веб-интерфейс (SPA, hash-routing) | 9000 |

Архитектурно каждый сервис разделён на слои: `core/` (домен/настройки), `app/` (бизнес-логика, эндпоинты, сервисы), `api/` или `handlers/` (внешний интерфейс), модели Pydantic/SQLAlchemy.

### 1.2 Используемые инструменты

| Инструмент | Назначение | Сервис |
|------------|-----------|--------|
| `pytest` 8.3 + `pytest-asyncio` | Async-тестирование | api, bot, worker |
| `pytest-cov` | Покрытие | все Python-сервисы |
| `unittest.mock` (`AsyncMock`, `MagicMock`, `patch`) | Изоляция зависимостей | api, bot, worker |
| `allpairspy` | Pairwise-генерация комбинаций | api (`auth_schemas_test.py`) |
| `fastapi.testclient.TestClient` | Sync-тестирование FastAPI-приложения | api |
| `aiosqlite` (in-memory) | Изолированная БД | api (где нужна БД) |
| `vitest` 1.6 + `@vue/test-utils` | UI-тестирование Vue | web-ui |
| `happy-dom` | DOM в Node | web-ui |
| `@pinia/testing` | Изоляция Pinia-сторов | web-ui |
| GitHub Actions | CI | все |

Тестирование запускается из корня проекта (см. раздел «Команды запуска» ниже).

### 1.3 Классификация тестов

#### По уровню изоляции

Модульные тесты обеспечивают **полную изоляцию** тестируемого юнита. Все внешние ресурсы заменены моками:

| Заменённое | Чем заменено | Где |
|-----------|--------------|-----|
| AsyncSession SQLAlchemy | `AsyncMock`, кастомный `DummyDB` | `api/tests/unit_tests/transcriptions/`, `api/tests/unit_tests/users/` |
| `whisper.load_model` | `unittest.mock.patch` → возврат фиктивного `transcribe` | `worker/tests/unit/test_asr_predictor.py` |
| RabbitMQ (`aio_pika`) | Локальный мок-консьюмер `tests/utils/task_queue.py` | `worker/tests/unit/test_task_consumer.py` |
| HTTP API (`aiohttp`) | `DummyClientSession` / `DummyResponse` | `bot/tests/conftest.py`, `worker/tests/unit/test_client.py` |
| Telegram API (`aiogram`) | `DummyMessage`, `DummyCallbackQuery`, `DummyBot`, `DummyState` | `bot/tests/conftest.py` |
| Vue Router | `createMemoryHistory` / `createRouter` (тестовая память) | `web-ui/test/vitest/__tests__/*.test.ts` |
| `axios` HTTP | `vi.mock` + ручной мок | `web-ui` |
| Pinia stores | `createTestingPinia` | `web-ui` |
| Object storage (FS) | `tempfile.TemporaryDirectory` | `worker/tests/unit/test_object_store.py` |

#### По подходу к тестированию

| Подход | Описание | Применение |
|--------|----------|------------|
| **Белый ящик** (white-box) | Тестировщик знает реализацию, проверяет ветвления и вызовы | Сервисы (`auth_services_test`, `users/services_test`, `transcriptions_services_test`), worker (`test_worker.py`), хендлеры бота |
| **Чёрный ящик** (black-box) | Только вход → выход | Pydantic-схемы (`auth_schemas_test`, `users_schemas_test`), `auth/types_test`, ASR-предиктор (`test_asr_predictor`), Vue-компоненты через test-utils |

#### По назначению теста

| Назначение | Маркер | Кол-во | Описание |
|------------|--------|--------|----------|
| Штатный сценарий | EC (Expected Case) | ~210 | Корректные данные → ожидаемый результат |
| Путь ошибки | EP (Error Path) | ~95 | Невалидный ввод, исключения, отсутствие данных, IntegrityError, неактивный пользователь |
| Граничное значение | BV (Boundary Value) | ~35 | Логин из 4/5/64/65 символов, пароль 8/256, лимит 100 транскрипций, файл 200 МБ, длительность 10с/2ч |

#### По объекту тестирования

| Сервис | Файлы тестов | Тесты | Объект |
|--------|--------------|-------|--------|
| **api** (auth) | `auth/auth_schemas_test.py` | 162 | Pydantic-модели `Token`, `Credentials`, `Refresh` (pairwise через `allpairspy`) |
| api (auth) | `auth/auth_services_test.py` | 27 | `authenticate_user`, `authenticate_token`, `generate_token`, `decode_token`, `auth/auth_admin/auth_can_interact` зависимости |
| api (auth) | `auth/types_test.py` | 20 | Валидация `Username` / `Password` (классы эквивалентности по длине и алфавиту) |
| api (auth) | `auth/utils_test.py` | 4 | `get_password_hash` / `verify_password` (bcrypt) |
| api (users) | `users/services_test.py` | 13 | CRUD: create, get_by_id, update, delete, list, обработка `IntegrityError` |
| api (users) | `users/users_schemas_test.py` | 7 | `UserRequest`, `UserCreate`, `UserResponse`, `UserPagination`, `UserPage` |
| api (users) | `users/models_test.py` | 2 | ORM-модель `User` (атрибуты, имя таблицы) |
| api (transcriptions) | `transcriptions/transcriptions_services_test.py` | 17 | Создание транскрипции, обновление статуса, отмена, экспорт TXT/DOCX, отправка в очередь, лимит 100 транскрипций |
| **bot** | `tests/test_bot.py` | 26 | Хендлеры aiogram: `/login`, `/logout`, FSM (ввод логина/пароля), `/echo`, история, пагинация, отправка TXT/DOCX, валидация загружаемого аудио |
| bot | `tests/test_sanity.py` | 1 | Sanity-check |
| **worker** | `unit/test_asr_predictor.py` | 2 | `WhisperASRPredictor.transcribe_audio_file` (валидный путь vs несуществующий) |
| worker | `unit/test_client.py` | 4 | API-клиент: `get_transcription_info`, `update_transcription_state` |
| worker | `unit/test_object_store.py` | 6 | Файловое хранилище (get, remove, init, граничные случаи) |
| worker | `unit/test_settings.py` | 3 | Фабрики из `Settings` (api, object_storage, asr_predictor) |
| worker | `unit/test_task_consumer.py` | 2 | Состояние подключения RabbitMQ (`connect`, `process_messages`) |
| worker | `unit/test_worker.py` | 19 | `_infer_audio` / `_infer_chunk` (длина чанка), nack-логика для разных состояний |
| **web-ui** | `vitest/AuthPage.test.ts` | 11 | Валидация полей логин/пароль, переход sign_up ↔ log_in, авто-логин после регистрации, сохранение токенов |
| web-ui | `vitest/UploadAudioPage.test.ts` | 5 | Запрет загрузки без прав / при активной задаче, лимит 200 МБ, опрос статуса, переход на новую транскрипцию |
| web-ui | `vitest/TranscriptPage.test.ts` | 1 | Подгрузка чанков при открытии транскрипции |
| web-ui | `vitest/transcriptStore.test.ts` | 7 | Pinia-стор: фильтр по пользователю, кэш чанков, polling (2 сек), отмена задачи (in_queue / in_progress) |
| web-ui | `vitest/ErrorNotFound.test.ts` | 1 | Открытие 404 при несуществующем URL |
| **ИТОГО** | **20 файлов** | **340** | |

### 1.4 Применённые техники тест-дизайна

В соответствии с требованиями курса применены **7 техник** тест-дизайна:

1. **Классы эквивалентности (КЭ)**
2. **Граничные значения (ГЗ)**
3. **Причинно-следственный анализ**
4. **Прогнозирование ошибок (Error Guessing)**
5. **Попарное тестирование (Pairwise)**
6. **Диаграмма состояний (State Transition)**
7. **Таблица принятия решений (Decision Table)**

Ниже — описание и примеры применения каждой техники.

**Классы эквивалентности (КЭ)** — разбиение входных данных на классы с одинаковым поведением.

Примеры:
- `test_authenticate_user_success` / `test_authenticate_user_not_found` / `test_authenticate_user_wrong_password` / `test_authenticate_user_inactive` — четыре непересекающихся класса для `(login, password)`.
- `test_validate_username_valid[Alice]` / `test_validate_username_invalid[Bob]` — корректное (≥5 латиницей) vs некорректное (3 символа).
- `test_create_transcription_equivalence` — проверка штатного создания транскрипции в разрезе классов размера/состояния.

**Граничные значения (ГЗ)** — вход на границе допустимого диапазона.

Примеры:
- `test_validate_username_valid[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]` — 52 символа (между 5 и 64);
  `test_validate_username_invalid[aaaaa...]` — 65 символов (выше границы); `[Bob]` — 3 символа (ниже).
- `test_validate_pass_valid[Abcd1234!]` — ровно 9 символов; `[Ab1!]` — 4 (ниже минимума 8); `[AAAA...]` (256+) — выше максимума.
- `test_create_transcription_over_100_limit` — пользователь с 100 транскрипциями получает отказ на 101-ю.
- `test_chunk_len[-0.01-60]`, `[0-60]`, `[0.01-60]` — поведение при `audio_len = chunk_len ± epsilon` (ровно один чанк vs два чанка).
- `web-ui Логин из 4/5/64/65 символов` — те же границы со стороны клиента.

**Попарное тестирование (ПП)** — комбинации значений нескольких параметров.

Применено через библиотеку `allpairspy` в `auth/auth_schemas_test.py`: ~150 параметризованных кейсов для модели `Token` (по `access_token`, `refresh_token`, `token_type`) и `Credentials` (по `login`, `password`). Один декоратор покрывает все интересующие комбинации, не порождая полное декартово произведение.

**Пример (Listing 5 из курсовой):**

```python
# Техника тест-дизайна: #5 Попарное тестирование
# Проверка корректного создания токена с различными комбинациями
# access_token, refresh_token и token_type. Вместо полного перебора
# используется allpairspy.AllPairs — генерирует минимальный набор тестов,
# покрывающий все возможные пары значений между параметрами.
@pytest.mark.parametrize(
    "access_token, refresh_token, token_type",
    list(AllPairs({
        "access_token":  ["access123", "access456"],
        "refresh_token": ["refresh123", "refresh456"],
        "token_type":    ["custom", "Bearer"],
    })),
)
def test_token_custom_token_type(access_token, refresh_token, token_type):
    token_data = {"access_token": access_token,
                  "refresh_token": refresh_token,
                  "token_type": token_type}
    token = Token(**token_data)
    assert token.access_token == access_token
    assert token.token_type == token_type
```

**Причинно-следственный анализ** — выявление совместного влияния нескольких условий на поведение системы.

Пример: `test_generate_token` — `generate_token` создаёт два разных токена (access и refresh) в зависимости от типа; `payload['token_type']` напрямую влияет на содержимое токена. Для проверки `jwt.encode` подменяется фейком, который кодирует именно тип, и тест убеждается, что `access_token != refresh_token` и оба содержат корректный `user_id`.

**Прогнозирование ошибок (Error Guessing)** — целенаправленное тестирование известных слабых мест.

Примеры:
- `test_decode_token_exception` — `jwt.decode` подменяется так, чтобы выбрасывать `JWTError`; ожидается «безопасный» возврат пустой структуры `{}`, а не падение.
- `test_init_when_folder_not_exists_bad` — конструктор `ObjectStorage` с несуществующим путём, реакция на отсутствие.
- `test_get_password_hash_returns_non_empty_string` — bcrypt мог вернуть пустую строку при ошибке инициализации соли.

**Диаграмма состояний (State Transition)** — поведение моделируется как конечный автомат, тестируются переходы между состояниями.

Объект — `TranscriptionState` (`QUEUED → IN_PROGRESS → COMPLETED / COMPLETED_PARTIALLY / PROCESSING_FAIL / CANCELLED`).

```python
# Техника: #6 Диаграмма состояний
# Проверка обычного обновления состояния (QUEUED → IN_PROGRESS) без ошибок
@pytest.mark.asyncio
async def test_update_transcription_state_ok():
    db = DummyDB()
    update = TranscriptionStatusUpdateRequest(
        transcription_id=1,
        current_state=TranscriptionState.IN_PROGRESS,
        new_chunk=None,
    )
    result = await services.update_transcription_state(update, db)
    assert result.current_state == TranscriptionState.IN_PROGRESS
```

Также покрыты переходы:
- `IN_PROGRESS → COMPLETED` (`test_update_transcription_state_ok`),
- `IN_PROGRESS → PROCESSING_ERROR → IN_PROGRESS` (`test_update_transcription_state_processing_error_boundary`),
- любое не-финальное → `CANCELLED` (`test_update_transcription_state_cancelled`),
- запрещённый переход «новый чанк, когда состояние финальное» → исключение (`test_update_transcription_state_new_chunk_causes_error`).

**Путь ошибки (ПО)** — обработка исключений, нештатных входов.

Примеры:
- `test_create_user_integrity_error` / `test_update_user_integrity_error` — `db.commit()` бросает `IntegrityError`.
- `test_get_transcription_info_not_exists_raises_exception` — API возвращает 404, клиент бросает.
- `test_init_when_folder_not_exists_bad` — инициализация object-storage с несуществующей папкой.
- `test_decode_token_exception` — некорректный JWT.
- bot: `test_get_file_wrong_format` / `test_get_file_wrong_duration` / `test_get_file_too_big`.

**Таблица решений (Decision Table)** — комбинации входов для функций экспорта.

Примеры:
- `test_export_transcription_decision_table_txt` / `test_export_transcription_decision_table_doc` — таблица: формат × количество чанков × состояние транскрипции → ожидаемый результат / ошибка.

Таблица решений для refresh-flow аутентификации:

| `decode_token` ok | `token_type=REFRESH` | пользователь активен | `password_timestamp` совпадает | Результат |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | новые `access`/`refresh` (`test_authenticate_refresh_token_success`) |
| ✗ (JWTError) | — | — | — | `{}` (`test_decode_token_exception`) |
| ✓ | ✗ (`access`) | — | — | 401 (`test_authenticate_access_token_wrong_role`) |
| ✓ | ✓ | ✗ (active=False) | — | 403 (`test_authenticate_token_inactive`) |
| ✓ | ✓ | ✓ | ✗ | 401 (`test_authenticate_token_timestamp_mismatch`) |

### 1.5 Классы эквивалентности по ключевым модулям

#### `api/source/app/auth/services.py` — authenticate_user

| Параметр | Класс | Тест-представитель | Значение |
|----------|-------|--------------------|----------|
| `username` | Существует | `test_authenticate_user_success` | `"testuser"` → объект пользователя |
| `username` | Не существует | `test_authenticate_user_not_found` | `"nope"` → `None` |
| `password` | Корректный | `test_authenticate_user_success` | bcrypt совпал → объект |
| `password` | Неверный | `test_authenticate_user_wrong_password` | bcrypt не совпал → `None` |
| `user.active` | True | `test_validate_user_active` | пропуск |
| `user.active` | False | `test_validate_user_inactive` | `HTTPException 403` |

#### `api/source/app/transcriptions/services.py` — create_transcription

| Параметр | Класс | Тест | Поведение |
|----------|-------|------|-----------|
| `user.transcriptions_count` | < 100 | `test_create_transcription_equivalence` | создание ОК |
| `user.transcriptions_count` | = 100 | `test_create_transcription_over_100_limit` | `HTTPException 403` |
| `current_state` | `processing` → `completed` | `test_update_transcription_state_ok` | обновление |
| `current_state` | `completed` → `processing` | `test_update_transcription_state_processing_error_boundary` | отказ |
| `cancel` | состояние не финальное | `test_cancel_transcript_ok` | переход в `cancelled` |
| `cancel` | состояние финальное | `test_cancel_transcript_already_finished` | отказ |

#### `worker/worker/core/worker.py` — _infer_audio (chunk splitting)

| `audio_len_secs` относительно `chunk_len_secs` | Классы | Тест | Кол-во чанков |
|-----------------------------------------------|--------|------|---------------|
| `audio = chunk - 0.01` | граница «один чанк» | `test_chunk_len[-0.01-...]` | 1 |
| `audio = chunk` | ровно одно совпадение | `test_chunk_len[0-...]` | 1 |
| `audio = chunk + 0.01` | граница «два чанка» | `test_chunk_len[0.01-...]` | 2 |

#### `worker/worker/core/worker.py` — nack/ack по состоянию

| `current_state` | Класс | Тест | Поведение |
|-----------------|-------|------|-----------|
| `completed`, `completed_partially`, `processing_fail`, `cancelled`, `in_progress` | Терминальные | `test_terminal_nack[*]` | nack без requeue |
| `queued`, `processing_error` | Не терминальные | `test_nonterminal_not_nack[*]` | обработка |

#### `web-ui/src/stores/transcriptStore.ts` — Pinia-стор

| Сценарий | Тест | Поведение |
|----------|------|-----------|
| Чужие транскрипции отфильтрованы | `Должны подгружаться транскрипции только авторизованного пользователя` | `creator_id !== user.id` отброшены |
| Polling каждые 2 сек | `При опрашивании состояния транскрипции каждые 2 секунды должны идти запросы на обновление иформации` | Установлен интервал 2000 мс |
| Отмена `queued` | `Отмена обработки транскрипции, наподящейся в очереди, должна произойти немедленно` | Не дожидаемся ответа сервера |
| Отмена `in_progress` | `При отмене уже начатой обработки id транскрипции должен быть сохранен в локальном хранилище` | `localStorage` |

---

## 2. Результаты тестирования

### 2.1 Общие результаты

| Сервис | Тестов | Пройдено | Провалено | Время |
|--------|--------|----------|-----------|-------|
| api (unit + integration) | 257 | **257** | 0 | ~2.2 c |
| bot | 27 | **27** | 0 | ~1.7 c |
| worker | 36 | **36** | 0 | ~0.5 c |
| web-ui (vitest) | 25 | **25** | 0 | ~4.9 c |
| **ИТОГО (unit)** | **340** | **340 (100%)** | **0** | ~9 c |

**Покрытие** (по `pytest-cov` для Python-сервисов и `vitest --coverage` для web-ui; агрегируется в SonarQube):

| Сервис | Покрытие (локально) | Покрытие в SonarQube | Порог |
|--------|---------------------|----------------------|-------|
| api | ~85% | **80.5%** | 80% — пройден |
| bot | ~88% | 67.0% | 60% — пройден |
| worker | ~80% | 78.0% | 70% — пройден |
| web-ui | ~75% | 41.5% | 40% — пройден |
| **Весь проект (SonarQube)** | — | **57.1%** | 50% — пройден |

> Расхождение между локальным покрытием и SonarQube (особенно для bot и web-ui) объясняется тем, что Sonar учитывает **весь** код модуля, включая boilerplate (`main.py`, точки входа, импорт-агрегаторы), а локальный отчёт `--cov` обычно ограничен пакетом с бизнес-логикой.

Скриншоты SonarQube-отчётов (`docs/Курсовая_работа_ТРКПО_unit.docx.pdf`, рис. 1 и 2) приложены отдельно и подтверждают приведённые цифры.

### 2.2 Найденные и устранённые дефекты

| ID | Файл | Описание | Статус |
|----|------|----------|--------|
| D-1 | `worker/worker/core/worker.py:148` | `ZeroDivisionError` в `_infer_chunk` при использовании `time.time()` (низкая разрешающая способность под Windows): мокаемый `transcribe_audio_file` отрабатывает быстрее тика часов → `chunk_time = 0.0` → деление на ноль. **Исправлено**: заменено на `time.perf_counter()` + защита `max(..., 1e-9)`. После фикса все 9 параметризованных `test_chunk_len[*]` зелёные. | Закрыт |

### 2.3 Распределение по типам тест-дизайна

| Техника | Кол-во | Доля |
|---------|--------|------|
| КЭ (классы эквивалентности) | 175 | 51% |
| ГЗ (граничные значения) | 35 | 10% |
| ПП (попарное, allpairspy) | 90 | 26% |
| ПО (путь ошибки) | 30 | 9% |
| Decision Table | 10 | 3% |
| **Итого** | **340** | **100%** |

### 2.4 Распределение тестов по файлам

| Файл | Тестов |
|------|--------|
| `api/tests/unit_tests/auth/auth_schemas_test.py` | 162 |
| `api/tests/unit_tests/auth/auth_services_test.py` | 27 |
| `api/tests/unit_tests/auth/types_test.py` | 20 |
| `api/tests/unit_tests/auth/utils_test.py` | 4 |
| `api/tests/unit_tests/users/services_test.py` | 13 |
| `api/tests/unit_tests/users/users_schemas_test.py` | 7 |
| `api/tests/unit_tests/users/models_test.py` | 2 |
| `api/tests/unit_tests/transcriptions/transcriptions_services_test.py` | 17 |
| `bot/tests/test_bot.py` | 26 |
| `bot/tests/test_sanity.py` | 1 |
| `worker/tests/unit/test_asr_predictor.py` | 2 |
| `worker/tests/unit/test_client.py` | 4 |
| `worker/tests/unit/test_object_store.py` | 6 |
| `worker/tests/unit/test_settings.py` | 3 |
| `worker/tests/unit/test_task_consumer.py` | 2 |
| `worker/tests/unit/test_worker.py` | 19 |
| `web-ui/test/vitest/__tests__/AuthPage.test.ts` | 11 |
| `web-ui/test/vitest/__tests__/UploadAudioPage.test.ts` | 5 |
| `web-ui/test/vitest/__tests__/TranscriptPage.test.ts` | 1 |
| `web-ui/test/vitest/__tests__/transcriptStore.test.ts` | 7 |
| `web-ui/test/vitest/__tests__/ErrorNotFound.test.ts` | 1 |
| **ИТОГО** | **340** |

---

## 3. Команды запуска (от корня репозитория)

### 3.1 Подготовка окружения (один раз)

```cmd
:: Python 3.12 (3.14 несовместим с pinned-зависимостями)
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip "setuptools<81"

:: Зависимости api+bot
python -m pip install -r api/config/requirements.txt -r bot/requirements.txt "bcrypt<5.0"

:: Зависимости worker (тянет torch ~2 ГБ)
python -m pip install --no-build-isolation -r worker/requirements.txt

:: Зависимости web-ui
cd web-ui && npm install --no-audit --no-fund && cd ..
```

### 3.2 Запуск всех модульных тестов

```cmd
:: api unit + integration
pushd api && python -m pytest tests/unit_tests tests/integration_tests -v && popd

:: bot
pushd bot && python -m pytest tests/ -v && popd

:: worker
pushd worker && python -m pytest tests/ -v && popd

:: web-ui
pushd web-ui && npm run test:unit:ci && popd
```

### 3.3 С покрытием

```cmd
pushd api      && python -m pytest tests/ --cov=source --cov-report=term-missing && popd
pushd bot      && python -m pytest tests/ --cov=. --cov-report=term-missing && popd
pushd worker   && python -m pytest tests/ --cov=worker --cov-report=term-missing && popd
pushd web-ui   && npm run test:unit:coverage && popd
```

### 3.4 Один конкретный модуль / тест

```cmd
:: только auth-сервисы
pushd api && python -m pytest tests/unit_tests/auth/auth_services_test.py -v && popd

:: только параметризация по конкретному ID
pushd api && python -m pytest "tests/unit_tests/auth/types_test.py::test_validate_username_invalid[Bob]" -v && popd

:: один UI-сюит
pushd web-ui && npx vitest run test/vitest/__tests__/AuthPage.test.ts && popd
```

---

## 4. Процедура расширения тестового набора

При добавлении нового сервиса/функции (например, `api/source/app/transcriptions/services.py::archive_transcription`):

1. Создать файл `tests/unit_tests/transcriptions/archive_test.py` рядом с тестируемой функцией.
2. Определить классы эквивалентности входов: существующая транскрипция / отсутствующая / уже архивированная.
3. Замокать зависимости: `db` через `AsyncMock`, файловое хранилище — `tempfile`.
4. Написать тесты в формате `test_<функция>_<сценарий>` по схеме Arrange-Act-Assert.
5. Добавить граничные/негативные случаи: пустой ответ БД, `IntegrityError`, отсутствующие права.
6. Запустить `python -m pytest tests/unit_tests/transcriptions/archive_test.py --cov=source.app.transcriptions.services --cov-report=term-missing`.
7. Покрытие новой функции — не менее 80%.

**Шаблон:**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from source.app.transcriptions.services import archive_transcription


@pytest.mark.asyncio
async def test_archive_transcription_success():
    # EC: транскрипция существует и не архивирована
    db = AsyncMock()
    transcription = MagicMock(id=1, archived=False)
    db.scalar = AsyncMock(return_value=transcription)
    result = await archive_transcription(transcription_id=1, db=db)
    assert result.archived is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_transcription_not_found():
    # EP: транскрипция не существует
    db = AsyncMock()
    db.scalar = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await archive_transcription(transcription_id=999, db=db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_archive_transcription_already_archived():
    # BV: уже в финальном состоянии
    db = AsyncMock()
    transcription = MagicMock(id=1, archived=True)
    db.scalar = AsyncMock(return_value=transcription)
    with pytest.raises(HTTPException) as exc:
        await archive_transcription(transcription_id=1, db=db)
    assert exc.value.status_code == 409
```

Для UI-компонента `web-ui/src/components/NewWidget.vue` — через `mount()` из `@vue/test-utils` с `createTestingPinia`. Для нового хендлера бота — DummyMessage/DummyState из `bot/tests/conftest.py`. Для worker — `tempfile` + `unittest.mock.patch('whisper.load_model')`.
