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
import aiohttp

auth_router = Router()

# { id: { name: string
#         access_token: string
#         refresh_token: string
#       }
# }
users: dict[int, dict[str, str]] = {}


async def send_refresh_request(url, body):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            return await response.json()  # or response.text() if you expect plain text


async def refresh_token(user_id: int):
    user_data = users.get(user_id)
    refresh_token = user_data.get("refresh_token")  # type: ignore
    url = f"http://localhost:8000/auth/refresh"  # Replace with your internal server URL
    body = {"refresh_token": refresh_token}
    resp = await send_refresh_request(url, body)
    # TODO обратотать момент, когда refresh_token Не сработает - взять новый новый
    # access и refresh через send_login_request
    access_token = resp.get("access_token")
    refresh_token = resp.get("refresh_token")
    users[user_id]["access_token"] = access_token
    users[user_id]["refresh_token"] = refresh_token


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


async def send_login_request(username: str, password: str):
    url = f"http://localhost:8000/auth/login"  # Replace with your internal server URL

    body = {"username": username, "password": password}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            return await response.json()  # or response.text() if you expect plain text


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

            # Проверить, есть ли есть такой пользователь+пароль в API
            print(f"SENDING REQUEST WITH\nNAME: {state_data.get('name')}\nPASS: {user_password}")
            resp = await send_login_request(state_data.get("name"), user_password)  # type: ignore
            print(resp)

            # Если пользователя нет, сказать что неверные данные
            # {'detail': 'Incorrect username or password'}
            resp_detail = resp.get("detail", None)
            if resp_detail == "Incorrect username or password":
                await message.answer(f"Incorrect Username or Password")
            else:
                # Если есть, то вытащить из полученного ответа "access_token" и "refresh_token"
                #  и записать их вместе с именем в мапу
                # {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJwYXNzd29yZF90aW1lc3RhbXAiOjE3MzM3NzE2NjguOTEzNjIyLCJleHAiOjE3MzM3NzUzMTcsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.B3jEi3Huc_dKi78EHmWRzSl9fJ6EfNd8eRga70iMDYI', 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJwYXNzd29yZF90aW1lc3RhbXAiOjE3MzM3NzE2NjguOTEzNjIyLCJleHAiOjE3MzYzNjU1MTcsInRva2VuX3R5cGUiOiJyZWZyZXNoIn0.HtkWNfssUt9kOPHorjDX4KW6mAQ7jnnKunriunVKomg', 'token_type': 'bearer'}
                access_token = resp["access_token"]
                refresh_token = resp["refresh_token"]
                name = state_data.get("name")

                await message.answer(f"Good. You are logged in as {name}")
                user = message.from_user
                if user is None:
                    # TODO: some handling
                    # but seems like this arm is never gonna be reached
                    pass
                else:
                    # get keys we want to store
                    users[user.id] = {  # type: ignore
                        "name": name,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
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
