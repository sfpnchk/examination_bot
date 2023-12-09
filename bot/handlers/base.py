from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp


@dp.message_handler(commands=["cancel"], state="*")
async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Відмінено")
