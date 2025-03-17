from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

app = FastAPI()


@app.get("/transcriptions")
async def list_transcriptions(page: int = 1, size: int = 10):
    """
    Допустим, тут мы можем имитировать получение списка транскрипций
    по базе (упрощённо).
    """
    if page < 1 or size < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination params")
    return {"page": page, "size": size, "total": 100, "pages": 10, "transcriptions": []}


@app.post("/transcript/export")
async def export_transcript(task_id: int, format: str):
    if format not in ["doc", "txt"]:
        raise HTTPException(status_code=422, detail="Invalid format")
    if task_id < 0:
        raise HTTPException(status_code=400, detail="Invalid task id")
    return {"message": "exported"}


client = TestClient(app)


def test_list_transcriptions_ok():
    """
    КЛАССЫ ЭКВИВАЛЕНТНОСТИ: «хорошие» значения page/size
    """
    resp = client.get("/transcriptions", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["size"] == 10


def test_list_transcriptions_boundary():
    """
    ГРАНИЧНЫЕ ЗНАЧЕНИЯ:
    Если передать page=0, должны получить HTTP 422.
    """
    resp = client.get("/transcriptions", params={"page": 0, "size": 10})
    assert resp.status_code == 422


def test_export_transcript_equivalence():
    """
    КЛАССЫ ЭКВИВАЛЕНТНОСТИ: стандартные корректные значения.
    """
    resp = client.post("/transcript/export", params={"task_id": 1, "format": "txt"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "exported"


def test_export_transcript_invalid_format():
    """
    ТАБЛИЦА ПРИНЯТИЯ РЕШЕНИЙ:
    Если format не входит в ["doc", "txt"], возвращаем 422.
    """
    resp = client.post("/transcript/export", params={"task_id": 1, "format": "pdf"})
    assert resp.status_code == 422


def test_export_transcript_invalid_task_id():
    """
    ПРОГНОЗИРОВАНИЕ ОШИБОК:
    Если task_id < 0, возвращаем 400.
    """
    resp = client.post("/transcript/export", params={"task_id": -1, "format": "doc"})
    assert resp.status_code == 400
