from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp
from bot.db.decorators import session_decorator
from bot.db.models import Discipline
from bot.enums import DisciplineActionEnum
from bot.filters.admin import IsSuperAdmin
from bot.kb.admin_kb import discipline_callback, discipline_edit_callback, get_discipline_kb, edit_discipline_kb
from bot.states import DisciplineState


@dp.callback_query_handler(
    IsSuperAdmin(), discipline_callback.filter(action=DisciplineActionEnum.view_sub_category.value)
)
@session_decorator(add_param=False)
async def discipline_list(cq: types.CallbackQuery) -> None:
    kb = await get_discipline_kb()
    await cq.message.answer(
        "Меню дисциплін", reply_markup=kb
    )
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), discipline_callback.filter(action=DisciplineActionEnum.create.value)
)
@session_decorator(add_param=False)
async def create_discipline_btn(cq: types.CallbackQuery) -> None:
    await DisciplineState.name.set()
    await cq.message.answer("Введіть назву дисципліни:")
    await cq.answer()


@dp.message_handler(IsSuperAdmin(), state=DisciplineState.name)
@session_decorator(add_param=False)
async def load_name(msg: types.Message, state: FSMContext):
    if await Discipline.exists(None, name=msg.text):
        return await msg.answer("Дисципліна з такою назвою вже існує, введіть іншу")
    async with state.proxy() as data:
        data["name"] = msg.text
    await DisciplineState.short_description.set()
    await msg.reply("Ведіть короткий опис дисципліни:")


@dp.message_handler(IsSuperAdmin(), state=DisciplineState.short_description)
@session_decorator(add_param=False)
async def load_short_description(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    short_description = msg.text
    await Discipline.create(**data, short_description=short_description)
    await state.finish()
    await msg.answer("Дисципліну створено ✅")


@dp.callback_query_handler(
    IsSuperAdmin(), discipline_callback.filter(action=DisciplineActionEnum.delete.value)
)
@session_decorator(add_param=False)
async def delete_discipline(cq: types.CallbackQuery, callback_data: dict) -> None:
    discipline = await Discipline.get(int(callback_data["discipline_id"]))
    await discipline.delete()
    await cq.message.answer("Дисципліну видалено ✅")



@dp.callback_query_handler(
    IsSuperAdmin(), discipline_callback.filter(action=DisciplineActionEnum.edit.value)
)
@session_decorator()
async def discipline_edit_btn(
    cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:

    discipline_id = callback_data.get("discipline_id")
    async with state.proxy() as data:
        data["discipline_id"] = discipline_id

    discipline = await Discipline.get(int(data["discipline_id"]))

    await cq.message.answer(
        f"Оберіть що хочете відредагувати в «{discipline.name}»", reply_markup = edit_discipline_kb(int(callback_data["discipline_id"]))
                            )

@dp.callback_query_handler(
    IsSuperAdmin(), discipline_edit_callback.filter(action=DisciplineActionEnum.edit_name.value)
)
@session_decorator()
async def discipline_edit_name(
    cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await DisciplineState.edit_name.set()

    discipline_id = callback_data.get("discipline_id")
    async with state.proxy() as data:
        data["discipline_id"] = discipline_id

    discipline = await Discipline.get(int(data["discipline_id"]))

    await cq.message.answer(f"Поточна назва дисципліни:\n{discipline.name}")
    await cq.message.answer("Введіть нову назву дисципліни\nДля відміни - /cancel")


@dp.message_handler(IsSuperAdmin(), state=DisciplineState.edit_name)
@session_decorator()
async def discipline_edit_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        discipline_id = int(data["discipline_id"])
    edited_discipline = await Discipline.get(discipline_id)

    await edited_discipline.update(name=msg.text)
    await state.finish()
    await msg.answer("Назву дисципліни відредаговано ✅")


@dp.callback_query_handler(
    IsSuperAdmin(), discipline_edit_callback.filter(action=DisciplineActionEnum.edit_short_description.value)
)
@session_decorator()
async def discipline_edit_short_description(
    cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await DisciplineState.edit_short_description.set()

    discipline_id = callback_data.get("discipline_id")
    async with state.proxy() as data:
        data["discipline_id"] = discipline_id

    discipline = await Discipline.get(int(data["discipline_id"]))

    await cq.message.answer(f"Поточна коротка назва:\n{discipline.short_description}")
    await cq.message.answer("Введіть новий короткий опис дисципліни \nДля відміни - /cancel")


@dp.message_handler(IsSuperAdmin(), state=DisciplineState.edit_short_description)
@session_decorator()
async def discipline_edit_short_description(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        discipline_id = int(data["discipline_id"])
    edited_discipline = await Discipline.get(discipline_id)

    await edited_discipline.update(short_description=msg.text)
    await state.finish()
    await msg.answer("Короткий опис дисципліни відредаговано ✅")

