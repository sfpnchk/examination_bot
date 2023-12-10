from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp
from bot.db.decorators import session_decorator
from bot.db.models import Answer, Question
from bot.enums import AnswerActionEnum
from bot.filters.admin import IsSuperAdmin
from bot.kb.admin_kb import (
    question_callback,
    skip_photo_kb,
    answer_callback,
    get_question_kb,
    get_answer_kb,
    answer_edit_callback,
)
from bot.states import AnswerState


@dp.callback_query_handler(
    IsSuperAdmin(),
    answer_callback.filter(action=AnswerActionEnum.create_right_answer.value),
)
@session_decorator()
async def create_right_answer(
    cq: types.CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    async with state.proxy() as data:
        data["question_id"] = int(callback_data["question_id"])
    await AnswerState.right_answer.set()
    await cq.message.answer("Введіть одну правильну відповідь")
    await cq.answer()


@dp.message_handler(IsSuperAdmin(), state=AnswerState.right_answer)
@session_decorator(add_param=False)
async def right_answer(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if await Answer.exists(None, question_id=data["question_id"], text=msg.text):
        return await msg.answer("Така відповідь вже існує, введіть іншу")
    data["text"] = msg.text
    data["is_correct"] = True
    await Answer.create(**data)
    await msg.reply("Відповідь додано ✅")
    await state.finish()


@dp.callback_query_handler(
    IsSuperAdmin(),
    answer_callback.filter(action=AnswerActionEnum.create_wrong_answer.value),
)
@session_decorator()
async def create_wrong_answer(
    cq: types.CallbackQuery, state: FSMContext, callback_data: dict
) -> None:
    async with state.proxy() as data:
        data["question_id"] = int(callback_data["question_id"])
    await AnswerState.wrong_answer.set()
    await cq.message.answer("Введіть одну неправильну відповідь")
    await cq.answer()


@dp.message_handler(IsSuperAdmin(), state=AnswerState.wrong_answer)
@session_decorator(add_param=False)
async def wrong_answer(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if await Answer.exists(None, question_id=data["question_id"], text=msg.text):
        return await msg.answer("Така відповідь вже існує, введіть іншу")
    data["text"] = msg.text
    data["is_correct"] = False
    await Answer.create(**data)
    await msg.reply("Відповідь додано ✅")
    await state.finish()


@dp.callback_query_handler(
    IsSuperAdmin(), answer_callback.filter(action=AnswerActionEnum.detail.value)
)
@session_decorator()
async def answer_list(cq: types.CallbackQuery, callback_data: dict) -> None:
    answers = await Answer.get_list(
        Answer.question_id == int(callback_data["question_id"])
    )
    questions = await Question.get(int(callback_data["question_id"]))
    await cq.message.answer(f"Відповіді до питання «{questions.text}»")
    for answer in answers:
        if answer.is_correct:
            await cq.message.answer(
                f"Правильна відповідь: {answer.text}",
                reply_markup=get_answer_kb(answer.id),
            )
        else:
            await cq.message.answer(
                f"Неправильна відповідь: {answer.text}",
                reply_markup=get_answer_kb(answer.id),
            )
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), answer_edit_callback.filter(action=AnswerActionEnum.delete.value)
)
@session_decorator()
async def delete_answer(cq: types.CallbackQuery, callback_data: dict) -> None:
    answer = await Answer.get(int(callback_data["answer_id"]))
    await answer.delete()
    await cq.message.answer("Відповідь видалено ✅")
    await cq.answer()


@dp.callback_query_handler(
    IsSuperAdmin(), answer_edit_callback.filter(action=AnswerActionEnum.edit_text.value)
)
@session_decorator()
async def answer_edit_text(
    cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    await AnswerState.edit_text.set()

    answer_id = callback_data.get("answer_id")
    async with state.proxy() as data:
        data["answer_id"] = answer_id

    answer = await Answer.get(int(data["answer_id"]))

    await cq.message.answer(f"Поточний текст відповіді:\n{answer.text}")
    await cq.message.answer("Введіть новий текст відповіді \nДля відміни - /cancel")


@dp.message_handler(IsSuperAdmin(), state=AnswerState.edit_text)
@session_decorator()
async def answer_edit_text(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answer_id = int(data["answer_id"])
    edited_answer = await Answer.get(answer_id)

    await edited_answer.update(text=msg.text)
    await state.finish()
    await msg.answer("Текст відповіді відредаговано ✅")
