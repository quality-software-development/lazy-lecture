from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

# Создаём простое FastAPI-приложение, имитирующее поведение ваших эндпоинтов.
app = FastAPI()


# Эндпоинт для получения списка транскрипций
@app.get("/transcriptions")
async def list_transcriptions(page: int = 1, size: int = 10):
    # Граничные значения: если page или size меньше 1 — ошибка валидации.
    if page < 1 or size < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination params")
    # Классы эквивалентности: корректные параметры возвращают стандартную структуру.
    return {"page": page, "size": size, "total": 100, "pages": 10, "transcriptions": []}


# Эндпоинт для экспорта транскрипции
@app.post("/transcript/export")
async def export_transcript(task_id: int, format: str):
    # Таблица принятия решений:
    #  - Если формат не равен "doc" или "txt", возвращается ошибка 422.
    #  - Если task_id < 0, возвращается ошибка 400.
    if format not in ["doc", "txt"]:
        raise HTTPException(status_code=422, detail="Invalid format")
    if task_id < 0:
        raise HTTPException(status_code=400, detail="Invalid task id")
    return {"message": "exported"}


client = TestClient(app)


def test_list_transcriptions_ok():
    """
    **Техника: Классы эквивалентности.**
    Проверяем эндпоинт /transcriptions с корректными параметрами (page=1, size=10).
    Ожидаемый результат — успешный ответ (HTTP 200) с корректными значениями.
    """
    resp = client.get("/transcriptions", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["size"] == 10


def test_list_transcriptions_boundary():
    """
    **Техника: Граничные значения.**
    Передаём недопустимое значение (page=0) и ожидаем ошибку валидации (HTTP 422).
    """
    resp = client.get("/transcriptions", params={"page": 0, "size": 10})
    assert resp.status_code == 422


def test_export_transcript_equivalence():
    """
    **Техника: Классы эквивалентности.**
    Проверяем эндпоинт /transcript/export с корректными значениями (task_id=1, format="txt").
    Ожидаем успешный ответ (HTTP 200) с сообщением "exported".
    """
    resp = client.post("/transcript/export", params={"task_id": 1, "format": "txt"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "exported"


def test_export_transcript_invalid_format():
    """
    **Техника: Таблица принятия решений.**
    Если формат не входит в допустимый набор ["doc", "txt"] (например, "pdf"),
    ожидаем ошибку (HTTP 422).
    """
    resp = client.post("/transcript/export", params={"task_id": 1, "format": "pdf"})
    assert resp.status_code == 422


def test_export_transcript_invalid_task_id():
    """
    **Техника: Прогнозирование ошибок.**
    Если task_id меньше нуля, ожидаем ошибку (HTTP 400).
    """
    resp = client.post("/transcript/export", params={"task_id": -1, "format": "doc"})
    assert resp.status_code == 400
