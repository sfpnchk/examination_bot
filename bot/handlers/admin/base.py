from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp
from bot.filters.admin import IsSuperAdmin
from bot.kb.admin_kb import admin_kb


@dp.message_handler(IsSuperAdmin(), commands="admin", state="*")
async def admin_menu(msg: types.Message, state: FSMContext) -> None:
    await state.finish()
    await msg.answer("Вітаю! Ви потрапили до режиму адміністратора.", reply_markup=admin_kb)
