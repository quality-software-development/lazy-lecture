from .settings import API_BASE_URL

from aiogram import F, Router, Bot

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import aiohttp
from handlers.auth import refresh_token

from handlers.auth import users
import tempfile

upload_router = Router()


class UploadForm(StatesGroup):
    waiting_for_file = State()
    file_uploaded = State()


async def get_account_info(url, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()  # or response.text() if you expect plain text


@upload_router.message(Command("upload"))
async def upload(message: Message, state: FSMContext) -> None:
    user = message.from_user
    user_id = user.id  # type: ignore
    user = users.get(user_id)

    if user is not None:
        # ЕСЛИ ЮЗЕР НЕ АКТИВЕЙТЕД ОТПРАВЛЯТЬ ЕМУ ССЫЛКУ НА ТГ ИЛЬИ
        url = f"{API_BASE_URL}/auth/info"
        access_token = users.get(user_id).get("access_token")  # type: ignore
        acc_info = await get_account_info(url, access_token)
        activated = acc_info["can_interact"]
        if not activated:
            keyboard = []
            buttons = []
            buttons.append(
                InlineKeyboardButton(
                    text="Запросить доступ к транскрипции",
                    url="https://t.me/ll_requests",
                )
            )
            keyboard.append(buttons)
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await message.answer(
                "Попросите активировать свой аккаунт у администрации",
                reply_markup=inline_keyboard,
            )
        else:
            # Если пользователь вошёл в систему, сказать отправляй файл и ждать файла.
            await state.set_state(UploadForm.waiting_for_file)
            await message.answer("Отправь мне .mp3 файл")
    else:
        # Если пользователь не вошёл в систему,
        # команда /upload выводит сообщение о необходимости входа в систему.
        await message.answer("Войдите в систему. /login")


@upload_router.message(UploadForm.waiting_for_file)
async def get_file(message: Message, state: FSMContext, bot: Bot) -> None:
    audio = message.audio
    if audio is None or audio.mime_type.split("+")[-1] != "audio/mpeg":  # type: ignore
        await message.answer("Мы не получили .mp3 Файла. Присылайте только .mp3 файлы.")
        return
    if audio.duration < 10 or audio.duration > 2 * 60 * 60:
        await message.answer("Аудиозапись должна длиться от 10 секунд до 2 часов.")
        return
    file_size_mb = int(audio.file_size * 1e-6)  # type: ignore
    if file_size_mb > 20:
        await message.answer(f"Чтобы загружать файлы больше 20 мегабайт переходите на сайт Lazy Lecture.")
        return
    file_id = audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Download the file
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/file/bot{bot.token}/{file_path}") as resp:
            if resp.status == 200:
                user = message.from_user
                user_id = user.id  # type: ignore
                await refresh_token(user_id)
                user = users.get(user_id)
                bearer_token = users.get(user_id).get("access_token")  # type: ignore
                headers = {
                    "Authorization": f"Bearer {bearer_token}",
                    "accept": "application/json",
                    # "Content-Type": "multipart/form-data",
                }

                file_content = await resp.read()
                # Prepare the multipart/form-data request
                form = aiohttp.FormData()
                form.add_field(
                    "audiofile",
                    file_content,
                    filename=audio.file_name,
                    content_type="audio/mpeg",
                )
                # Send the file to the server
                async with session.post(f"{API_BASE_URL}/upload-audiofile", data=form, headers=headers) as upload_resp:
                    # print(upload_resp.status)
                    # print(await upload_resp.text())
                    data = await upload_resp.json()
                    # print(f"WATAFAK{data}")
                    errorr = data.get("detail")
                    if errorr is not None:
                        if data["detail"].split(" ")[0] == "Transcription":
                            print("YOU ARE LOH EBANIY. WAIT UNTIL THE QUEUED WILL BE ANTIQUEUED")
                            await message.answer(
                                "Невозможно обрабатывать более одного файла одновременно. Либо отмените обработку текущей транскрипции, либо дождитесь конца обработки."
                            )
                    else:
                        task_id = data["task_id"]
                        # {"message":"File uploaded successfully","task_id":9,"file":"object_storage/4.mp3"}
                        if upload_resp.status == 200:
                            # Отправляем сообщение с кнопкой по нажатию на которую отсылаем запрос на отмену обработки
                            #                      с кнопкой по нажатию на которую будет запрос на обновление статуса
                            # В самом сообщении будет написпан статус текстом
                            keyboard = []
                            buttons = []
                            buttons.append(
                                InlineKeyboardButton(
                                    text="Обновить статус",
                                    callback_data=f"check_status_{task_id}",
                                )
                            )
                            buttons.append(
                                InlineKeyboardButton(
                                    text="Отменить обработку",
                                    callback_data=f"cancel_task_{task_id}",
                                )
                            )
                            keyboard.append(buttons)
                            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
                            await message.answer(
                                "Файл поступил в обработку",
                                reply_markup=inline_keyboard,
                            )
                        else:
                            await message.answer("Ошибка при загрузке файла на сервер.")
            else:
                await message.answer("Ошибка при загрузке файла.")


async def get_task_status(url, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()  # or response.text() if you expect plain text


@upload_router.callback_query(F.data.startswith("check_status_"))
async def check_task_status(callback: CallbackQuery) -> None:
    task_id = int(callback.data.split("_")[-1])  # type: ignore
    # print(f"TAKSID UPDATE CHECKSTAUS: {task_id}")
    user_id = callback.from_user.id
    await refresh_token(user_id)
    url = f"{API_BASE_URL}/transcript/info?transcript_id={task_id}"
    access_token = users.get(user_id).get("access_token")  # type: ignore
    state = await get_task_status(url, access_token)
    new_status = state["current_state"]
    if new_status == "completed":
        await callback.message.edit_text("Статус: completed")  # type: ignore
    else:
        await callback.message.edit_text(f"Статус: {new_status}", reply_markup=callback.message.reply_markup)  # type: ignore
    await callback.answer()


async def post_cancel_task(url, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as response:
            return await response.text()  # or response.text() if you expect plain text


@upload_router.callback_query(F.data.startswith("cancel_task_"))
async def cancel_task(callback: CallbackQuery) -> None:
    task_id = int(callback.data.split("_")[-1])  # type: ignore
    # print(f"CANCELLING TASK ID: {task_id}")
    user_id = callback.from_user.id
    await refresh_token(user_id)
    url = f"{API_BASE_URL}/transcript/cancel?transcript_id={task_id}"
    access_token = users.get(user_id).get("access_token")  # type: ignore
    resp = await post_cancel_task(url, access_token)
    if resp == "OK":
        await callback.message.edit_text("Статус: Отменён")  # type: ignore
    elif resp == '{"detail":"You can\'t cancel a finished job"}':
        await callback.message.edit_text("Статус: completed")  # type: ignore
    await callback.answer()
