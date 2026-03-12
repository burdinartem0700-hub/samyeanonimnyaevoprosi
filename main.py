import asyncio
import json
import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.heandlers import router
from app.DARABASE import init_db

back_send = InlineKeyboardMarkup(inline_keyboard =[
    [InlineKeyboardButton(text = "Отменить", callback_data="back_sen")]
])

async def main():
    bot = Bot(token='8569542955:AAHz8MZHouGM8Vy52Aa5_47iFvWXIXh-U1I')
    dp = Dispatcher(storage=MemoryStorage())
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")