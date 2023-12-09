from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp
from bot.db.decorators import session_decorator
from bot.db.models import Discipline, Question, Answer
from bot.db.queries import get_random_question
from bot.enums import DisciplineActionEnum, QuestionActionEnum, AnswerActionEnum
from bot.kb.user_kb import get_user_disciplines_kb, get_disciplines_question_kb, discipline_callback, question_callback, \
    get_answers, answers_callback
from bot.states import UserMenuStepState


@dp.message_handler(commands=["start"], state="*")
@session_decorator()
async def start_menu(msg: types.Message):
    kb = await get_user_disciplines_kb()
    await msg.answer("Вітаю 🤚🏼\n"
                     "Даний бот🤖 розрахований для підготовки абітурієнтів до вступних іспитів.")
    await msg.answer("Оберіть дисципліну", reply_markup=kb)


@dp.callback_query_handler(discipline_callback.filter(action=DisciplineActionEnum.view_list.value))
@session_decorator()
async def discipline_list(cq: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    discipline_id = callback_data.get("discipline_id")
    async with state.proxy() as data:
        data["discipline_id"] = discipline_id

    discipline = await Discipline.get(int(data["discipline_id"]))
    await cq.message.answer(
        f"Ви обрали дисципліну «{discipline.name}»\nОберіть наступну дію",
        reply_markup=await get_disciplines_question_kb(discipline.id)
    )
    await cq.answer()


@dp.callback_query_handler(question_callback.filter(action=QuestionActionEnum.view.value))
@session_decorator(add_param=True)
async def question(session, cq: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    discipline_id = callback_data.get("discipline_id")

    question = await get_random_question(session, int(discipline_id))
    await cq.message.answer(question.text, reply_markup=await get_answers(question.id))
    await cq.answer()


@dp.callback_query_handler(answers_callback.filter(action=AnswerActionEnum.show_answer.value))
@session_decorator()
async def answer(cq: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    answer_id = callback_data.get("answer_id")
    async with state.proxy() as data:
        data["answer_id"] = answer_id

    answer = await Answer.get(int(data["answer_id"]))

    if answer.is_correct:
        await cq.answer("✅ Відповідь правильна")
        await cq.message.edit_text(answer.text+"\n✅ Відповідь правильна")
    else:
        await cq.answer("❌ Відповідь неправильна!")
        await cq.message.edit_text(answer.text+"\n❌ Відповідь неправильна")

    await cq.answer()
