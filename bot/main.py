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
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = getenv("BOT_TOKEN") or "Token was not found in the environment"

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user = message.from_user
    reply_text = ""
    match user:
        case None:
            reply_text = f"Привет, студент!"
        case User():
            reply_text = f"Привет, студент {html.bold(user.full_name)}!"

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


class LoginForm(StatesGroup):
    name = State()
    password = State()


@dp.message(Command("login"))
async def login(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginForm.name)
    await message.answer(
        f"Got you! Let's start the login process\nWhat is your username?",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(LoginForm.name)
async def process_login_name(message: Message, state: FSMContext) -> None:
    username = message.text
    match username:
        case None:
            await message.answer(
                "You must write your name as a text message broooo\nTry again"
            )
        case str():
            # TODO: Handle cases when name doesn't pass requirements
            await state.update_data(name=username)
            await state.set_state(LoginForm.password)
            await message.answer("Good. What is your password?")


@dp.message(LoginForm.password)
async def process_login_password(message: Message, state: FSMContext) -> None:
    user_password = message.text
    match user_password:
        case None:
            await message.answer(
                "You must write your password as a text message broooo\nTry again"
            )
        case str():
            # TODO: Handle cases when password doesn't pass requirements
            await state.update_data(password=user_password)
            user_data = await state.get_data()
            await state.clear()
            await message.answer(f"Good. You are logged in as {user_data}")


@dp.message(Command("logout"))
async def logout(message: Message) -> None:
    await message.answer(
        f"Got you! You are logged out", reply_markup=ReplyKeyboardRemove()
    )


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
