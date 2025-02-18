import asyncio
import tempfile
from pathlib import Path
from datetime import datetime

import pytest
import aiohttp

class DummyUser:
    def __init__(self, user_id, first_name="Test"):
        self.id = user_id
        self.first_name = first_name


class DummyMessage:
    def __init__(self, text="", message_id=1, from_user=None, chat_id=1, audio=None):
        self.text = text
        self.message_id = message_id
        self.from_user = from_user or DummyUser(123)
        self.chat = type("DummyChat", (), {"id": chat_id})()
        self.audio = audio
        self.reply_markup = None

    async def answer(self, text, reply_markup=None):
        self.answered_text = text
        self.reply_markup = reply_markup
        return text

    async def delete_message(self, message_id):
        self.deleted_message_id = message_id
        return

    async def send_copy(self, chat_id):
        return self

    async def answer_document(self, input_file, caption=""):
        self.document_sent = (input_file, caption)
        return

    async def edit_reply_markup(self, reply_markup):
        self.reply_markup = reply_markup
        return

    async def edit_text(self, text, reply_markup=None):
        self.edited_text = text
        self.reply_markup = reply_markup
        return


class DummyState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def set_state(self, state):
        self.state = state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def clear(self):
        self.data = {}
        self.state = None


class DummyCallbackQuery:
    def __init__(self, data, message, from_user):
        self.data = data
        self.message = message
        self.from_user = from_user

    async def answer(self):
        self.answered = True
        return


class DummyBot:
    def __init__(self, token="dummy_token"):
        self.token = token

    async def get_file(self, file_id):
        class DummyFile:
            file_path = "dummy/path/file.mp3"

        return DummyFile()


class DummyResponse:
    def __init__(self, json_data=None, text_data="", status=200, raw=b""):
        self._json = json_data
        self._text = text_data
        self.status = status
        self._raw = raw

    async def json(self):
        return self._json

    async def text(self):
        return self._text

    async def read(self):
        return self._raw

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class DummyClientSession:
    def __init__(self, response=None):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def post(self, url, json=None, data=None, headers=None):
        return DummyResponse(json_data=self.response, status=200, raw=b"dummy_file_content")

    def get(self, url, headers=None):
        return DummyResponse(json_data=self.response, status=200, raw=b"dummy_file_content")
