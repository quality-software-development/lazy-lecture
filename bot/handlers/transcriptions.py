import os
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from aiogram.types.callback_query import CallbackQuery
import json
from datetime import datetime

from handlers.auth import users, refresh_token
import aiohttp

from .settings import API_BASE_URL

transcriptions_router = Router()

# Constants
TRANSCRIPTIONS_PER_PAGE = 5


async def send_history_request(url, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()  # or response.text() if you expect plain text


@transcriptions_router.message(Command("history"))
async def get_history(message: Message) -> None:
    user = message.from_user
    user_id = user.id  # type: ignore
    await refresh_token(user_id)
    url = f"{API_BASE_URL}/transcriptions?page=1"
    access_token = users.get(user_id).get("access_token")  # type: ignore
    # print("Sending history request:", access_token)
    data = await send_history_request(url, access_token)
    # print(data)
    # data = json.loads(mock_history) Fuck you MOCK. I dont need yoU!
    await send_transcriptions(message, data["transcriptions"], 0, False)


async def send_transcriptions(message, transcriptions: list, page: int, from_callback: bool) -> None:
    start_index = 0
    end_index = start_index + TRANSCRIPTIONS_PER_PAGE
    keyboard = []

    for transcription in transcriptions[start_index:end_index]:
        date_string = transcription["create_date"]
        formatted_date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y.%m.%d %H:%M:%S")
        # Create buttons for transcription, .txt, and .doc
        transcription_button = InlineKeyboardButton(
            text=f"{formatted_date_time} | {transcription['description']}",
            callback_data=f"transcription_{transcription['id']}",
        )
        # print("trans:", transcription_button)
        keyboard.append([transcription_button])

    # Pagination buttons
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(text="Previous", callback_data=f"page_{page - 1}"))
    pagination_buttons.append(InlineKeyboardButton(text="Next", callback_data=f"page_{page + 1}"))

    keyboard.append(pagination_buttons)

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if from_callback:
        await message.edit_reply_markup(reply_markup=inline_keyboard)
    else:
        await message.answer("Your transcriptions:", reply_markup=inline_keyboard)


@transcriptions_router.callback_query(F.data.startswith("page_"))
async def pagination_handler(callback: CallbackQuery) -> None:
    page = int(callback.data.split("_")[1])  # type: ignore
    print(f"Page: {page}")
    user_id = callback.from_user.id
    url = f"{API_BASE_URL}/transcriptions?page={page+1}"
    print(f"URL: {url}")
    access_token = users.get(user_id).get("access_token")  # type: ignore
    data = await send_history_request(url, access_token)
    transcriptions = data["transcriptions"]
    print(f"Data: {transcriptions}")
    # data = json.loads(mock_history)
    await send_transcriptions(callback.message, transcriptions, page, True)
    await callback.answer()  # Acknowledge the callback


@transcriptions_router.callback_query(F.data.startswith("transcription_"))
async def transcription_handler(callback: CallbackQuery) -> None:
    task_id = callback.data.split("_")[1]  # type: ignore

    # Ask user for format choice
    format_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Send as .txt", callback_data=f"send_txt_{task_id}"),
                InlineKeyboardButton(text="Send as .docx", callback_data=f"send_docx_{task_id}"),
            ]
        ]
    )

    await callback.message.answer("Choose a file format:", reply_markup=format_keyboard)  # type: ignore
    await callback.answer()


@transcriptions_router.callback_query(F.data.startswith("send_txt_"))
async def send_txt_file(callback: CallbackQuery) -> None:
    task_id = callback.data.split("_")[-1]  # type: ignore
    print(f"Retrieving txt of file {task_id}")

    print(cwd)
    # Here you would generate or retrieve the .txt file based on the task_id
    # file_path = f"{task_id}.txt"  # Example file path

    file_path = r"handlers/transcriptions/mock.txt"
    input_file = FSInputFile(file_path)

    await callback.message.answer_document(input_file, caption="Here is your .txt file.")  # type: ignore
    await callback.answer()


cwd = os.getcwd()


@transcriptions_router.callback_query(F.data.startswith("send_docx_"))
async def send_docx_file(callback: CallbackQuery) -> None:
    task_id = callback.data.split("_")[-1]  # type: ignore
    print(f"Retrieving docx of file {task_id}")
    # Here you would generate or retrieve the .docx file based on the task_id
    # file_path = f"{task_id}.docx"  # Example file path

    file_path = r"handlers/transcriptions/mock.docx"
    input_file = FSInputFile(file_path)

    # type: ignore
    await callback.message.answer_document(input_file, caption="Here is your .docx file.")  # type: ignore
    await callback.answer()
