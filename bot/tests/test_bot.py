import asyncio

import aiohttp
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


from tests.conftest import (
    DummyResponse,
    DummyClientSession,
    DummyState,
    DummyMessage,
    DummyUser,
    DummyCallbackQuery,
    DummyBot,
)
from handlers import auth, echo, transcriptions_history, upload_audiofile
from handlers.settings import API_BASE_URL


@pytest.mark.asyncio
async def test_send_refresh_request(monkeypatch):
    dummy_resp = {"access_token": "new_access", "refresh_token": "new_refresh"}

    async def dummy_post(url, json):
        return DummyResponse(json_data=dummy_resp)

    monkeypatch.setattr(aiohttp, "ClientSession", lambda: DummyClientSession(response=dummy_resp))
    result = await auth.send_refresh_request("http://dummy/api", {"refresh_token": "old_refresh"})
    assert result["access_token"] == "new_access"
    assert result["refresh_token"] == "new_refresh"


@pytest.mark.asyncio
async def test_refresh_token_updates_users(monkeypatch):
    user_id = 999
    auth.users[user_id] = {"name": "tester", "access_token": "old_access", "refresh_token": "old_refresh"}

    dummy_resp = {"access_token": "new_access", "refresh_token": "new_refresh"}
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: DummyClientSession(response=dummy_resp))
    await auth.refresh_token(user_id)
    assert auth.users[user_id]["access_token"] == "new_access"
    assert auth.users[user_id]["refresh_token"] == "new_refresh"


@pytest.mark.asyncio
async def test_login_command():
    state = DummyState()
    message = DummyMessage(text="/login", from_user=DummyUser(1))
    await auth.login(message, state)
    assert state.state == auth.LoginForm.name


@pytest.mark.asyncio
async def test_process_login_name_none():
    state = DummyState()
    message = DummyMessage(text=None, from_user=DummyUser(1))
    await auth.process_login_name(message, state)
    assert "You must write your name" in message.answered_text


@pytest.mark.asyncio
async def test_process_login_name_valid():
    state = DummyState()
    message = DummyMessage(text="username", message_id=10, from_user=DummyUser(1))
    await auth.process_login_name(message, state)
    data = await state.get_data()
    assert data["name"] == "username"
    assert data["name_message_id"] == 10
    assert state.state == auth.LoginForm.password


@pytest.mark.asyncio
async def test_send_login_request(monkeypatch):
    dummy_resp = {"access_token": "a", "refresh_token": "r"}
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: DummyClientSession(response=dummy_resp))
    result = await auth.send_login_request("user", "pass")
    assert result["access_token"] == "a"
    assert result["refresh_token"] == "r"


@pytest.mark.asyncio
async def test_process_login_password_invalid(monkeypatch):
    state = DummyState()
    await state.update_data(name="tester", name_message_id=11)
    message = DummyMessage(text="wrong_pass", message_id=12, from_user=DummyUser(1))

    async def dummy_send_login_request(username, password):
        return {"detail": "Incorrect username or password"}

    monkeypatch.setattr(auth, "send_login_request", dummy_send_login_request)
    await auth.process_login_password(message, state)
    assert "Неверное имя пользователя" in message.answered_text


@pytest.mark.asyncio
async def test_process_login_password_valid(monkeypatch):
    state = DummyState()
    await state.update_data(name="tester", name_message_id=11, password_message_id=12)
    message = DummyMessage(text="correct_pass", message_id=13, from_user=DummyUser(1))

    async def dummy_delete_message(message_id):
        message.chat.deleted_message_id = message_id

    message.chat.delete_message = dummy_delete_message
    dummy_resp = {"access_token": "access", "refresh_token": "refresh"}

    async def dummy_send_login_request(username, password):
        return dummy_resp

    monkeypatch.setattr(auth, "send_login_request", dummy_send_login_request)
    await auth.process_login_password(message, state)
    user_data = auth.users.get(1)
    assert user_data is not None
    assert user_data["access_token"] == "access"
    assert hasattr(message.chat, "deleted_message_id")


@pytest.mark.asyncio
async def test_logout_not_logged_in():
    state = DummyState()
    message = DummyMessage(text="/logout", from_user=DummyUser(100))
    if 100 in auth.users:
        del auth.users[100]
    await auth.logout(message, state)
    assert "не входили в систему" in message.answered_text


@pytest.mark.asyncio
async def test_logout_logged_in():
    state = DummyState()
    message = DummyMessage(text="/logout", from_user=DummyUser(200))
    auth.users[200] = {"name": "tester", "access_token": "a", "refresh_token": "r"}
    await auth.logout(message, state)
    assert state.state == auth.LogoutForm.confirms
    data = await state.get_data()
    assert data["user_id"] == 200


@pytest.mark.asyncio
async def test_confirms_logout_cancel():
    state = DummyState()
    await state.update_data(user_id=300)
    message = DummyMessage(text="Нет", from_user=DummyUser(300))
    await auth.confirms_logout(message, state)
    assert "не вышли из системы" in message.answered_text
    assert state.state is None


@pytest.mark.asyncio
async def test_confirms_logout_confirm():
    state = DummyState()
    await state.update_data(user_id=400)
    auth.users[400] = {"name": "tester", "access_token": "a", "refresh_token": "r"}
    message = DummyMessage(text="Да", from_user=DummyUser(400))
    await auth.confirms_logout(message, state)
    assert "Вы вышли из системы" in message.answered_text
    assert 400 not in auth.users


@pytest.mark.asyncio
async def test_echo_handler_success(monkeypatch):
    message = DummyMessage(text="echo", from_user=DummyUser(1))

    async def dummy_send_copy(chat_id):
        return message

    monkeypatch.setattr(message.chat, "id", 1)
    monkeypatch.setattr(message, "send_copy", dummy_send_copy)
    await echo.echo_handler(message)


@pytest.mark.asyncio
async def test_echo_handler_type_error(monkeypatch):
    message = DummyMessage(text="echo", from_user=DummyUser(1))

    async def dummy_send_copy(chat_id):
        raise TypeError

    monkeypatch.setattr(message.chat, "id", 1)
    monkeypatch.setattr(message, "send_copy", dummy_send_copy)
    await echo.echo_handler(message)
    assert "Nice try!" in message.answered_text


@pytest.mark.asyncio
async def test_get_history_not_logged_in():
    message = DummyMessage(text="/history", from_user=DummyUser(500))
    if 500 in auth.users:
        del auth.users[500]
    await transcriptions_history.get_history(message)
    assert "Войдите в систему" in message.answered_text


@pytest.mark.asyncio
async def test_get_history_success(monkeypatch):
    user_id = 600
    auth.users[user_id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    message = DummyMessage(text="/history", from_user=DummyUser(user_id))
    monkeypatch.setattr(message.chat, "id", 1)
    monkeypatch.setattr(auth, "refresh_token", lambda uid: asyncio.sleep(0))
    dummy_data = {
        "transcriptions": [
            {
                "id": 1,
                "create_date": "2025-02-18T10:00:00.000000",
                "description": "Desc1",
                "current_state": "completed",
            },
            {
                "id": 2,
                "create_date": "2025-02-18T11:00:00.000000",
                "description": "Desc2",
                "current_state": "in_progress",
            },
        ]
    }

    async def dummy_send_history_request(url, token):
        return dummy_data

    monkeypatch.setattr(transcriptions_history, "send_history_request", dummy_send_history_request)

    async def dummy_send_transcriptions(msg, transcriptions, page, from_callback):
        msg.transcriptions = transcriptions

    monkeypatch.setattr(transcriptions_history, "send_transcriptions", dummy_send_transcriptions)
    await transcriptions_history.get_history(message)
    assert hasattr(message, "transcriptions")
    assert len(message.transcriptions) <= transcriptions_history.TRANSCRIPTIONS_PER_PAGE


@pytest.mark.asyncio
async def test_pagination_handler(monkeypatch):
    user_id = 700
    auth.users[user_id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=DummyUser(user_id))
    callback = DummyCallbackQuery("page_2", dummy_message, DummyUser(user_id))
    dummy_data = {
        "transcriptions": [
            {
                "id": i,
                "create_date": "2025-02-18T10:00:00.000000",
                "description": f"Desc{i}",
                "current_state": "completed",
            }
            for i in range(1, 11)
        ]
    }

    async def dummy_send_history_request(url, token):
        return dummy_data

    monkeypatch.setattr(transcriptions_history, "send_history_request", dummy_send_history_request)

    async def dummy_send_transcriptions(msg, transcriptions, page, from_callback):
        msg.pagination = (transcriptions, page)

    monkeypatch.setattr(transcriptions_history, "send_transcriptions", dummy_send_transcriptions)
    await transcriptions_history.pagination_handler(callback)
    assert hasattr(dummy_message, "pagination")
    transcriptions, page = dummy_message.pagination
    assert page == 2


@pytest.mark.asyncio
async def test_transcription_handler(monkeypatch):
    user = DummyUser(800)
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("transcription_55", dummy_message, user)
    await transcriptions_history.transcription_handler(callback)
    assert dummy_message.reply_markup is not None


@pytest.mark.asyncio
async def test_send_txt_file_success(monkeypatch):
    user = DummyUser(900)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("send_txt_77", dummy_message, user)

    async def dummy_get_export_request(url, token):
        return b"dummy content"

    monkeypatch.setattr(transcriptions_history, "get_export_request", dummy_get_export_request)
    await transcriptions_history.send_txt_file(callback)
    assert hasattr(dummy_message, "document_sent")
    input_file, caption = dummy_message.document_sent
    assert caption == "Вот ваш .txt файл."


@pytest.mark.asyncio
async def test_send_txt_file_decode_error(monkeypatch):
    user = DummyUser(901)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("send_txt_88", dummy_message, user)

    async def dummy_get_export_request(url, token):
        return b"\xff\xff"

    monkeypatch.setattr(transcriptions_history, "get_export_request", dummy_get_export_request)
    await transcriptions_history.send_txt_file(callback)
    assert "Не удалось обработать файл" in dummy_message.answered_text


@pytest.mark.asyncio
async def test_send_docx_file_success(monkeypatch):
    user = DummyUser(902)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("send_docx_99", dummy_message, user)

    async def dummy_get_export_request(url, token):
        return b"dummy docx content"

    monkeypatch.setattr(transcriptions_history, "get_export_request", dummy_get_export_request)
    await transcriptions_history.send_docx_file(callback)
    assert hasattr(dummy_message, "document_sent")
    input_file, caption = dummy_message.document_sent
    assert caption == "Вот ваш .docx файл."


@pytest.mark.asyncio
async def test_upload_not_logged_in():
    state = DummyState()
    message = DummyMessage(text="/upload", from_user=DummyUser(1000))
    if 1000 in auth.users:
        del auth.users[1000]
    await upload_audiofile.upload(message, state)
    assert "Войдите в систему" in message.answered_text


@pytest.mark.asyncio
async def test_upload_inactive_user(monkeypatch):
    state = DummyState()
    user = DummyUser(1100)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}

    async def dummy_get_account_info(url, token):
        return {"can_interact": False}

    monkeypatch.setattr(upload_audiofile, "get_account_info", dummy_get_account_info)

    message = DummyMessage(text="/upload", from_user=user)
    await upload_audiofile.upload(message, state)
    assert message.reply_markup is not None


@pytest.mark.asyncio
async def test_get_file_wrong_format():
    state = DummyState()
    user = DummyUser(1200)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    # Передаём message без audio или с неправильным mime_type
    message = DummyMessage(text="dummy", from_user=user)
    message.audio = type(
        "Audio",
        (),
        {"mime_type": "audio/ogg", "duration": 30, "file_size": 1000000, "file_id": "fid", "file_name": "test.ogg"},
    )
    bot = DummyBot()
    await upload_audiofile.get_file(message, state, bot)
    assert "не получили .mp3 Файла" in message.answered_text


@pytest.mark.asyncio
async def test_get_file_wrong_duration():
    state = DummyState()
    user = DummyUser(1201)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    message = DummyMessage(text="dummy", from_user=user)
    message.audio = type(
        "Audio",
        (),
        {"mime_type": "audio/mpeg", "duration": 5, "file_size": 1000000, "file_id": "fid", "file_name": "test.mp3"},
    )
    bot = DummyBot()
    await upload_audiofile.get_file(message, state, bot)
    assert "Аудиозапись должна длиться" in message.answered_text


@pytest.mark.asyncio
async def test_get_file_too_big():
    state = DummyState()
    user = DummyUser(1202)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    message = DummyMessage(text="dummy", from_user=user)
    message.audio = type(
        "Audio",
        (),
        {
            "mime_type": "audio/mpeg",
            "duration": 60,
            "file_size": 30 * 10**6,
            "file_id": "fid",
            "file_name": "test.mp3",
        },
    )
    bot = DummyBot()
    await upload_audiofile.get_file(message, state, bot)
    assert "файлы больше 20 мегабайт" in message.answered_text


@pytest.mark.asyncio
async def test_get_file_success(monkeypatch):
    state = DummyState()
    user = DummyUser(1300)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    audio_obj = type(
        "Audio",
        (),
        {"mime_type": "audio/mpeg", "duration": 60, "file_size": 1000000, "file_id": "fid", "file_name": "test.mp3"},
    )
    message = DummyMessage(text="dummy", from_user=user)
    message.audio = audio_obj
    bot = DummyBot()

    async def dummy_get_file(fid):
        await asyncio.sleep(0)
        return type("DummyFile", (), {"file_path": "dummy/path/file.mp3"})

    monkeypatch.setattr(auth, "refresh_token", lambda uid: asyncio.sleep(0))
    monkeypatch.setattr(bot, "get_file", dummy_get_file)
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: DummyClientSession(response={"task_id": 999}))
    await upload_audiofile.get_file(message, state, bot)
    assert message.reply_markup is not None


@pytest.mark.asyncio
async def test_check_task_status(monkeypatch):
    user = DummyUser(1400)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("check_status_101", dummy_message, user)

    async def dummy_get_task_status(url, token):
        return {"current_state": "completed"}

    monkeypatch.setattr(upload_audiofile, "get_task_status", dummy_get_task_status)
    await upload_audiofile.check_task_status(callback)
    assert "completed" in dummy_message.edited_text


@pytest.mark.asyncio
async def test_cancel_task(monkeypatch):
    user = DummyUser(1500)
    auth.users[user.id] = {"name": "tester", "access_token": "access", "refresh_token": "refresh"}
    dummy_message = DummyMessage(text="dummy", from_user=user)
    callback = DummyCallbackQuery("cancel_task_202", dummy_message, user)

    async def dummy_post_cancel_task(url, token):
        return "OK"

    monkeypatch.setattr(upload_audiofile, "post_cancel_task", dummy_post_cancel_task)
    await upload_audiofile.cancel_task(callback)
    assert "Отменён" in dummy_message.edited_text
