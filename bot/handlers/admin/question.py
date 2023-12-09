from decimal import Decimal, DecimalException

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.core import dp
from bot.db.decorators import session_decorator
from bot.db.models import Discipline, Question
from bot.enums import DisciplineActionEnum, QuestionActionEnum
from bot.filters.admin import IsSuperAdmin
from bot.kb.admin_kb import discipline_callback, get_question_kb, question_callback, question_edit_callback, \
    skip_photo_kb, create_question_kb, edit_question_kb
from bot.states import QuestionState


class InvalidInput(Exception):
    pass


def validate_price(text):
    try:
        price = Decimal(text.replace(',', '.'))
    except DecimalException:
        raise InvalidInput("Введіть валідне цифрове значення")

    if price < 0:
        raise InvalidInput("Введіть позитивне значення")

    return price


@dp.callback_query_handler(
    IsSuperAdmin(), discipline_callback.filter(action=DisciplineActionEnum.detail.value)
)
@session_decorator()
async def question_list(cq: types.CallbackQuery, callback_data: dict) -> None:
    questions = await Question.get_list(Question.discipline_id == int(callback_data["discipline_id"]))
    discipline = await Discipline.get(int(callback_data["discipline_id"]))
    await cq.message.answer(f"Питання дисципліни «{discipline.name}»")
    for question in questions:
        if question.photo:
            media = types.MediaGroup()
            for photo_id in question.photo:
                media.attach_photo(photo_id)

            await cq.message.answer_media_group(media=media)
        await cq.message.answer(question.text,
                                reply_markup=get_question_kb(question.id))

    kb = create_question_kb(int(callback_data["discipline_id"]))
    await cq.message.answer("---------------------------------",
                            reply_markup=kb)
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), question_callback.filter(action=QuestionActionEnum.delete.value)
)
@session_decorator()
async def delete_question(cq: types.CallbackQuery, callback_data: dict) -> None:
    question = await Question.get(int(callback_data["question_id"]))
    await question.delete()
    await cq.message.answer("Питання видалено ✅")
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), question_callback.filter(action=QuestionActionEnum.create.value)
)
@session_decorator()
async def create_question(cq: types.CallbackQuery, state: FSMContext, callback_data: dict) -> None:
    async with state.proxy() as data:
        data["discipline_id"] = int(callback_data["discipline_id"])
    await QuestionState.photo.set()
    await cq.message.answer("Відправте фото до питання або пропустіть даний крок натиснувщи на кнопку нижче ", reply_markup=skip_photo_kb())


@dp.message_handler(state=QuestionState.photo, regexp="Пропустити фото")
async def skip_photo(msg: types.Message):
    await QuestionState.next()

    await msg.answer("Додавання фото пропущено", reply_markup=ReplyKeyboardRemove())
    await msg.reply("Введіть текст питання:")


@dp.message_handler(content_types=["photo"], state=QuestionState.photo)
async def load_photo(msg: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        data["photo"] = []
        if album := kwargs.get("album"):
            for obj in album:
                data["photo"].append(obj.photo[-1].file_id)
        else:
            data["photo"].append(msg.photo[-1].file_id)

    await QuestionState.next()
    await msg.reply("Введіть текст питання:", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=QuestionState.text)
@session_decorator()
async def load_text(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if await Question.exists(None, discipline_id=data["discipline_id"], text=msg.text):
        return await msg.answer("Таке питання вже існує")
    await Question.create(**data, text=msg.text)
    await state.finish()
    await msg.answer(f"Питання створено ✅\n")


@dp.callback_query_handler(
    IsSuperAdmin(), question_edit_callback.filter(action=QuestionActionEnum.detail.value)
)
@session_decorator()
async def question_details(
        cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    question_id = callback_data.get("question_id")
    async with state.proxy() as data:
        data["question_id"] = question_id

    question = await Question.get(int(data["question_id"]))
    await cq.message.answer(
        f"Оберіть дію для питання: \n «{question.text}»",
        reply_markup = edit_question_kb(int(callback_data["question_id"]))
    )
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), question_edit_callback.filter(action=QuestionActionEnum.edit_text.value)
)
@session_decorator()
async def question_edit_text(cq: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await QuestionState.edit_text.set()

    question_id = callback_data.get("question_id")
    async with state.proxy() as data:
        data["question_id"] = question_id

    question = await Question.get(int(data["question_id"]))

    await cq.message.answer(f"Поточний текст питання:\n{question.text}")
    await cq.message.answer("Введіть новий текст питання \nДля відміни - /cancel")


@dp.message_handler(IsSuperAdmin(), state=QuestionState.edit_text)
@session_decorator()
async def question_edit_text(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        question_id = int(data["question_id"])
    edited_question = await Question.get(question_id)

    await edited_question.update(text=msg.text)
    await state.finish()
    await msg.answer("Текст питання відредаговано ✅")


@dp.callback_query_handler(
    IsSuperAdmin(), question_edit_callback.filter(action=QuestionActionEnum.edit_photo.value)
)
async def question_edit_photo(
        cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await QuestionState.edit_photo.set()

    async with state.proxy() as data:
        data["question_id"] = callback_data.get("question_id")

    await cq.message.answer("Відправте фото \nДля відміни - /cancel", reply_markup=skip_photo_kb())


@dp.message_handler(content_types=["photo"], state=QuestionState.edit_photo)
@session_decorator()
async def update_photo(msg: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        question_id = int(data["question_id"])
    edited_question = await Question.get(question_id)

    photos = []
    if album := kwargs.get("album"):
        for obj in album:
            photos.append(obj.photo[-1].file_id)
    else:
        photos.append(msg.photo[-1].file_id)

    await edited_question.update(photo=photos)
    await state.finish()
    await msg.answer("Фото змінено ✅")
