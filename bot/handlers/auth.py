from aiogram import Router

from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

auth_router = Router()

# { id: { name: string } }
users: dict[int, dict[str, str]] = {}


class LoginForm(StatesGroup):
    name = State()
    password = State()
    name_message_id: int
    password_message_id: int


@auth_router.message(Command("login"))
async def login(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginForm.name)
    await message.answer(
        f"Got you! Let's start the login process\nWhat is your username?",
        reply_markup=ReplyKeyboardRemove(),
    )


@auth_router.message(LoginForm.name)
async def process_login_name(message: Message, state: FSMContext) -> None:
    username = message.text
    match username:
        case None:
            await message.answer("You must write your name as a text message broooo\nTry again")
        case str():
            await state.set_state(LoginForm.password)
            await state.update_data(name=username, name_message_id=message.message_id)
            await message.answer("Good. What is your password?")


@auth_router.message(LoginForm.password)
async def process_login_password(message: Message, state: FSMContext) -> None:
    user_password = message.text
    match user_password:
        case None:
            await message.answer("You must write your password as a text message broooo\nTry again")
        case str():
            await state.update_data(password=user_password, password_message_id=message.message_id)
            state_data = await state.get_data()
            await state.clear()
            await message.answer(f"Good. You are logged in as {state_data.get('name')}")
            user = message.from_user
            if user is None:
                # TODO: some handling
                # but seems like this arm is never gonna be reached
                pass
            else:
                # get keys we want to store
                users[user.id] = {"name": state_data.get("name")}  # type: ignore
                name_message_id = state_data.get("name_message_id")
                password_message_id = state_data.get("password_message_id")
                await message.chat.delete_message(message_id=name_message_id or 0)
                await message.chat.delete_message(message_id=password_message_id or 0)


class LogoutForm(StatesGroup):
    confirms = State()
    user_id: int


@auth_router.message(Command("logout"))
async def logout(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        # TODO: some handling
        pass
    else:
        user_id = user.id
        user_data = users.get(user_id)
        if user_data is None:
            await message.answer(f"You weren't logged in", reply_markup=ReplyKeyboardRemove())
        else:
            await state.set_state(LogoutForm.confirms)
            await state.update_data(user_id=user_id)
            await message.answer(
                f"Do you really want to logout?",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Yes"),
                            KeyboardButton(text="No"),
                        ]
                    ],
                    resize_keyboard=True,
                ),
            )


@auth_router.message(LogoutForm.confirms)
async def confirms_logout(message: Message, state: FSMContext) -> None:
    if message.text not in ["Yes", "yes", "Y", "y"]:
        await state.clear()
        await message.answer(
            f"Ok ok. You are not gonna be logged out",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        state_data = await state.get_data()
        user_id = state_data.get("user_id") or 0  # Because
        user_data = users.get(user_id) or {}  # User 100% exists
        await state.clear()
        await message.answer(
            f"Got you! You are no longer a {user_data['name']}\nYou are logged out",
            reply_markup=ReplyKeyboardRemove(),
        )
        del users[user_id]
