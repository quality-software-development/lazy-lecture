import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    User,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from handlers.auth import auth_router, users
from handlers.echo import echo_router

TOKEN = getenv("BOT_TOKEN") or "Token was not found in the environment"

dp = Dispatcher()
dp.include_routers(auth_router, echo_router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user = message.from_user
    reply_text = ""
    match user:
        case None:
            reply_text = f"Привет, студент!"
        case User():
            user_data = users.get(user.id)
            if user_data is None:
                reply_text = f"Привет, студент {html.bold(user.full_name)}!"
            else:
                reply_text = f"Привет, {html.bold(user_data['name'])}!"

    await message.answer(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="/login"),
                    KeyboardButton(text="/logout"),
                ]
            ]
        ),
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
