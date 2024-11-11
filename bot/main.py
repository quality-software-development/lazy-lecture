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

TOKEN = getenv("BOT_TOKEN") or "Token was not found in the environment"

dp = Dispatcher()
dp.include_routers(auth_router, echo_router)


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
    return username


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_name = await get_username(message)
    reply_text = ""
    match user_name:
        case "":
            reply_text = f"Привет, студент!"
        case _:
            reply_text = f"Привет, {html.bold(user_name)}!"

    await message.answer(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="/help"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@dp.message(Command("help"))
async def login(message: Message) -> None:
    await message.answer(
        """
First of all you can
    /login
Secondly, you can
    /upload your audio as an .mp3 file
    view /history of your transcriptions & get one in .txt or .doc
Finally, you can
    /logout
Secretly, you can check whose name you are logged in under.
    /whoami""",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command("whoami"))
async def whoami(message: Message) -> None:
    username = await get_username(message)
    await message.answer(f"you are logged in as {username}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
