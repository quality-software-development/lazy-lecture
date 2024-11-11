from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

transcriptions_router = Router()

# /history вызывает менюшку с 10 (или сколько максимум можно) с возможностью пагинации
# Возможность пролистывания
#
# При нажатии на кнопку транскрипции должно предлагаться в каком формате прислать её
# [.txt] или [.docx]


@transcriptions_router.message(Command("history"))
async def get_history(message: Message) -> None:
    message.answer("Your history")


async def upload_file(message: Message) -> None:
    pass
