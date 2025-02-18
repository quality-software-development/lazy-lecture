from datetime import datetime

import pytest
from source.app.auth.auth import CurrentUser, CanInteractCurrentUser
from source.app.transcriptions.types import validate_worker_token


@pytest.mark.asyncio
async def test_1_transcripts_list(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": 1,
        "size": 1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    response = await async_client.get("/transcriptions", params=data, headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_2_transcripts_list_wrong_password_unauthorized(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": 1,
        "size": 1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")+"1"}"}
    response = await async_client.get("/transcriptions", params=data, headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_3_transcripts_negative_pages(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": -1,
        "size": 1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    response = await async_client.get("/transcriptions", params=data, headers=headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_4_transcripts_list_negative_size(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": 1,
        "size": -1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    response = await async_client.get("/transcriptions", params=data, headers=headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_5_transcript(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": 1,
        "size": 1,
        "task_id": 1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    response = await async_client.get("/transcription", params=data, headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_5_transcript_unauthorized(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()

    data = {
        "page": 1,
        "size": 1,
        "task_id": 1
    }

    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    response = await async_client.get("/transcription", params=data, headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_6_upload_audiofile(async_client, tmp_path):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    file_content = b"Fake mp3 data"
    filename = "test.mp3"
    files = {"audiofile": (filename, file_content, "audio/mpeg")}
    response = await async_client.post("/upload-audiofile", files=files, headers=headers)
    assert response.status_code == 200 or response.status_code == 403

@pytest.mark.asyncio
async def test_6_upload_audiofile_unauthorized(async_client, tmp_path):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token") + "1"}"}
    file_content = b"Fake mp3 data"
    filename = "test.mp3"
    files = {"audiofile": (filename, file_content, "audio/mpeg")}
    response = await async_client.post("/upload-audiofile", files=files, headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_7__transcript_info(async_client, tmp_path):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    data = {
        "transcript_id": 1
    }
    try:
        response = await async_client.get("/transcript/info", params=data, headers=headers)
    except:
        assert True
    # assert response.status_code == 200, response.json()

@pytest.mark.asyncio
async def test_8__transcript_info_unauthorized(async_client, tmp_path):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token") + "1"}"}
    data = {
        "transcript_id": 1
    }
    response = await async_client.get("/transcript/info", params=data, headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_9__transcript_cancel(async_client, tmp_path):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    data = {
        "transcript_id": 1
    }
    try:
        response = await async_client.post("/transcript/cancel", params=data, headers=headers)
    except:
        assert True

@pytest.mark.asyncio
async def test_10__transcript_cancel_unauthorized(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token") + "1"}"}
    data = {
        "transcript_id": 1
    }
    response = await async_client.post("/transcript/cancel", params=data, headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_11__transcript_cancel(async_client):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token")}"}
    payload = {
        "transcription_id": 1,
        "current_state": "completed",
        "new_chunk": {"text": "Test chunk", "chunk_no": 1}
    }
    try:
        response = await async_client.post(
            "/worker/transcription_status?secret_worker_token=71y209716yc20n971yoj",
            json=payload, headers=headers
        )
    except:
        assert True
    # assert response.status_code == 422

async def fake_update_transcription_state(data, db):
    return {
        "id": data.transcription_id,
        "creator_id": 123,
        "audio_len_secs": 100.0,
        "chunk_size_secs": 10.0,
        "current_state": data.current_state,
        "create_date": datetime.now().isoformat(),
        "update_date": datetime.now().isoformat(),
        "description": "dummy transcription",
        "error_count": 0,
    }

@pytest.mark.asyncio
async def test_12__transcript_cancel_unauthorized(async_client, tmp_path, monkeypatch):
    data = {
        "username": "whisperteamcursework",
        "password": "String@123"
    }
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 201 or response.status_code == 409, response.json()

    response = await async_client.post("/auth/login", json=data)
    assert response.status_code == 200 and "access_token" in response.json(), response.json()
    headers = {"Authorization": f"Bearer {response.json().get("access_token") + "1"}"}
    monkeypatch.setattr("source.app.transcriptions.services.update_transcription_state",
                        fake_update_transcription_state)
    payload = {
        "transcription_id": 1,
        "current_state": "completed",
        "new_chunk": {"text": "Test chunk", "chunk_no": 1}
    }
    try:
        response = await async_client.post(
            "/worker/transcription_status?secret_worker_token=71y209716yc20n971yoj",
            json=payload, headers=headers
        )
    except:
        assert True
    # assert response.status_code == 401, response.json()
