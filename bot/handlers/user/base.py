from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.core import dp
from bot.db.base import Session, session_context
from bot.db.decorators import session_decorator
from bot.db.models import Discipline, Question, Answer, User, UserAnswer
from bot.db.queries import (
    get_question,
    get_user_active_disciplines,
    get_user_stats_for_discipline,
)
from bot.enums import DisciplineActionEnum, QuestionActionEnum, AnswerActionEnum
from bot.handlers.user.utils import send_question
from bot.kb.user_kb import (
    get_user_disciplines_kb,
    get_disciplines_question_kb,
    discipline_callback,
    question_callback,
    get_answers,
    answers_callback,
    get_main_menu_kb,
    get_discipline_for_statistics,
    discipline_statistics_callback,
)
from bot.states import UserMenuStepState


@dp.message_handler(commands=["start"], state="*")
@session_decorator()
async def start_menu(msg: types.Message):
    if not await User.get(msg.from_user.id):
        await User.create(
            id=msg.from_user.id,
            name=msg.from_user.full_name,
            user_name=msg.from_user.username,
        )

    kb = await get_user_disciplines_kb()
    await msg.answer(
        "Вітаю 🤚🏼\n"
        "Даний бот🤖 розрахований для підготовки абітурієнтів до вступних іспитів.",
        reply_markup=get_main_menu_kb(),
    )
    await msg.answer("Оберіть дисципліну", reply_markup=kb)


@dp.callback_query_handler(
    discipline_callback.filter(action=DisciplineActionEnum.view_list.value)
)
@session_decorator()
async def discipline_list(
        cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    discipline_id = callback_data.get("discipline_id")
    async with state.proxy() as data:
        data["discipline_id"] = discipline_id

    discipline = await Discipline.get(int(data["discipline_id"]))
    await cq.message.answer(
        f"Ви обрали дисципліну «{discipline.name}»📘\n\nОпис дисципліни:\n{discipline.short_description}\nОберіть наступну дію",
        reply_markup=await get_disciplines_question_kb(discipline.id),
    )
    await cq.answer()


@dp.callback_query_handler(
    question_callback.filter(action=QuestionActionEnum.view.value)
)
@session_decorator(add_param=True)
async def question(
        session, cq: types.CallbackQuery, callback_data: dict
) -> None:
    discipline_id = callback_data.get("discipline_id")
    await send_question(session, int(callback_data["discipline_id"]), cq.from_user.id)
    await cq.answer()


@dp.callback_query_handler(
    answers_callback.filter(action=AnswerActionEnum.show_answer.value)
)
@session_decorator(add_param=True)
async def answer(
        session, cq: types.CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    answer_id = callback_data.get("answer_id")
    async with state.proxy() as data:
        data["answer_id"] = answer_id

    answer = await Answer.get(int(data["answer_id"]))
    question = await Question.get(answer.question_id)

    if answer.is_correct:
        await cq.answer("✅ Відповідь правильна")
        await cq.message.edit_text(answer.text + "\n✅ Відповідь правильна")
    else:
        await cq.answer("❌ Відповідь неправильна!")
        await cq.message.edit_text(
            answer.text
            + f"\n❌ Відповідь неправильна\n   Матеріали:\n{question.material}"
        )

    await UserAnswer.create(user_id=cq.from_user.id, answer_id=answer.id)
    await session.commit()
    async with Session(expire_on_commit=False) as session:
        async with session.begin():
            token = session_context.set(session)
            try:
                await send_question(session, question.discipline_id, cq.from_user.id)
            finally:
                session_context.reset(token)

    await cq.answer()


@dp.message_handler(regexp="Дисципліни", state="*")
@session_decorator()
async def choice_discipline(msg: types.Message):
    kb = await get_user_disciplines_kb()

    await msg.answer("Оберіть дисципліну", reply_markup=kb)


@dp.message_handler(regexp="Статистика", state="*")
@session_decorator(add_param=True)
async def choice_statistic(session, msg: types.Message):
    user_active_disciplines = await get_user_active_disciplines(
        session, msg.from_user.id
    )
    kb = get_discipline_for_statistics(user_active_disciplines)
    await msg.answer("Оберіть дисципліну для перегляду статистики", reply_markup=kb)


@dp.callback_query_handler(discipline_statistics_callback.filter())
@session_decorator(add_param=True)
async def get_discipline_statics(
        session, callback_query: types.CallbackQuery, callback_data: dict
):
    discipline_id = int(callback_data["discipline_id"])
    statistics = await get_user_stats_for_discipline(
        session,
        user_id=callback_query.from_user.id,
        discipline_id=discipline_id,
    )
    discipline = await Discipline.get(discipline_id)

    await callback_query.message.answer(
        f"Статистика для дисципліни - {discipline.name}\n"
        f"Кількість питань в дисципліні - {statistics.discipline_question_count}\n"
        f"Кількість успішно пройдених питань - {statistics.discipline_right_answer_count}\n"
        f"Всього пройдено питань - {statistics.user_all_answers_count:}\n"
        f"Відсоток правильних відповідей - {statistics.right_answers_percent:.2f}%"
    )
    await callback_query.answer()
