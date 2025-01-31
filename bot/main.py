import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    User,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)

from handlers.auth import auth_router, users
from handlers.echo import echo_router
from handlers.transcriptions_history import transcriptions_router
from handlers.upload_audiofile import upload_router

TOKEN = getenv("BOT_TOKEN") or "Token was not found in the environment"

dp = Dispatcher()
dp.include_routers(auth_router, transcriptions_router, upload_router, echo_router)


async def get_username(message: Message) -> str:
    """If user is logged in will return his name.
    Otherwise, it will return his telegram nickname.
    In very unique case it will return empty string."""
    user = message.from_user
    username = ""
    match user:
        case None:
            username = ""
        case User():
            user_data = users.get(user.id)
            if user_data is None:
                username = user.full_name
            else:
                username = user_data["name"]
    return username  # type: ignore


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_name = await get_username(message)
    reply_text = ""
    match user_name:
        case "":
            reply_text = f"Привет, студент."
        case _:
            reply_text = f"Привет, {user_name}."

    reply_text += """
Инструкция по пользованию ботом

1. Вход в систему /login

2. Загрузка аудиозаписей /upload
Вы можете загрузить свои аудиозаписи в формате .mp3

3. Просмотр истории транскрипций /history
Для просмотра истории ваших транскрипций и их извлечения в форматах .txt или .docx

4. Выход из системы /logout

5. Проверка вашего имени пользователя /whoami
Чтобы узнать, под чьим именем вы вошли в систему

6. Получение помощи /help
Если вы хотите увидеть это сообщение снова
"""
    print("START")
    await message.answer(
        reply_text,
    )


@dp.message(Command("help"))
async def login(message: Message) -> None:
    await message.answer(
        """
Инструкция по пользованию ботом

1. Вход в систему /login

2. Загрузка аудиозаписей /upload
Вы можете загрузить свои аудиозаписи в формате .mp3

3. Просмотр истории транскрипций /history
Для просмотра истории ваших транскрипций и их извлечения в форматах .txt или .docx

4. Выход из системы /logout

5. Проверка вашего имени пользователя /whoami
Чтобы узнать, под чьим именем вы вошли в систему

6. Получение помощи /help
Если вы хотите увидеть это сообщение снова
""",
    )


@dp.message(Command("whoami"))
async def whoami(message: Message) -> None:
    for user_id, user_info in users.items():
        print(f"User ID: {user_id}")
        print(f"User Info: {user_info}")
        print()  # Print a newline for better readability
    username = await get_username(message)
    await message.answer(f"Вы вошли в систему как {username}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
