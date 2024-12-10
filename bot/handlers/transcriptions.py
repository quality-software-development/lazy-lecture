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

transcriptions_router = Router()

# Mock API response
mock_history = """
{
    "transcriptions": [
        {
            "task_id": "12345",
            "transcription": "This is the transcribed text of the audio.",
            "timestamp": "2024-10-22T12:34:56Z"
        },
        {
            "task_id": "12346",
            "transcription": "This is another transcribed text of a different audio.",
            "timestamp": "2024-10-21T11:33:45Z"
        },
        {
            "task_id": "12344",
            "transcription": "This is yet another transcribed text.",
            "timestamp": "2024-10-20T10:30:00Z"
        },
        {
            "task_id": "12347",
            "transcription": "The quick brown fox jumps over the lazy dog.",
            "timestamp": "2024-10-19T09:15:30Z"
        },
        {
            "task_id": "12348",
            "transcription": "Artificial intelligence is transforming the world.",
            "timestamp": "2024-10-18T08:45:12Z"
        },
        {
            "task_id": "12349",
            "transcription": "Data science combines statistics and computer science.",
            "timestamp": "2024-10-17T07:30:00Z"
        },
        {
            "task_id": "12350",
            "transcription": "Machine learning algorithms can improve over time.",
            "timestamp": "2024-10-16T06:20:45Z"
        },
        {
            "task_id": "12351",
            "transcription": "Natural language processing enables machines to understand human language.",
            "timestamp": "2024-10-15T05:10:30Z"
        },
        {
            "task_id": "12352",
            "transcription": "Cloud computing provides scalable resources over the internet.",
            "timestamp": "2024-10-14T04:00:00Z"
        },
        {
            "task_id": "12353",
            "transcription": "Blockchain technology ensures secure and transparent transactions.",
            "timestamp": "2024-10-13T03:50:15Z"
        },
        {
            "task_id": "12354",
            "transcription": "Cybersecurity is crucial for protecting sensitive information.",
            "timestamp": "2024-10-12T02:40:00Z"
        },
        {
            "task_id": "12355",
            "transcription": "The Internet of Things connects everyday devices to the internet.",
            "timestamp": "2024-10-11T01:30:00Z"
        }
    ]
}
"""

# Constants
TRANSCRIPTIONS_PER_PAGE = 5


async def send_history_request(url, bearer_token):
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()  # or response.text() if you expect plain text


@transcriptions_router.message(Command("history"))
async def get_history(message: Message) -> None:
    user = message.from_user
    user_id = user.id  # type: ignore
    await refresh_token(user_id)
    url = "http://localhost:8000/transcriptions?page=1"
    access_token = users.get(user_id).get('access_token')  # type: ignore
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
        formatted_date_time = datetime.strptime(
            date_string, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y.%m.%d %H:%M:%S")
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
        pagination_buttons.append(InlineKeyboardButton(
            text="Previous", callback_data=f"page_{page - 1}"))
    pagination_buttons.append(InlineKeyboardButton(
        text="Next", callback_data=f"page_{page + 1}"))

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
    url = f"http://localhost:8000/transcriptions?page={page+1}"
    print(f"URL: {url}")
    access_token = users.get(user_id).get('access_token')  # type: ignore
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

    await callback.message.answer(  # type: ignore
        "Choose a file format:", reply_markup=format_keyboard)
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

    await callback.message.answer_document(  # type: ignore
        input_file, caption="Here is your .txt file.")
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
    await callback.message.answer_document(  # type: ignore
        input_file, caption="Here is your .docx file.")
    await callback.answer()
