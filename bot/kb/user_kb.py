from random import shuffle

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from bot.db.models import Discipline, Question, Answer
from bot.enums import DisciplineActionEnum, QuestionActionEnum, AnswerActionEnum

discipline_callback = CallbackData("discipline", "action", "discipline_id")
question_callback = CallbackData("question", "action", "discipline_id")
answers_callback = CallbackData("answer", "action", "answer_id", "is_correct")


async def get_user_disciplines_kb():
    disciplines = await Discipline.get_list()
    kb = InlineKeyboardMarkup()
    for discipline in disciplines:
        kb.add(InlineKeyboardButton(discipline.name,
                                    callback_data=discipline_callback.new(
                                        action=DisciplineActionEnum.view_list.value,
                                        discipline_id=discipline.id)),

               )
    return kb


async def get_disciplines_question_kb(discipline_id: int):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("Перейти до питань",
                                callback_data=question_callback.new(action=QuestionActionEnum.view.value,
                                                                    discipline_id=discipline_id)),
           InlineKeyboardButton("Назад до вибору дисциплін",
                                callback_data=discipline_callback.new(action=DisciplineActionEnum.view_list.value,
                                                                      discipline_id=0))
           )
    return kb


async def get_answers(question_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    answers = await Answer.get_list(question_id=question_id)
    shuffle(answers)
    for answer in answers:
        kb.add(InlineKeyboardButton(answer.text,
                                    callback_data=answers_callback.new(
                                        action=AnswerActionEnum.show_answer.value,
                                        answer_id=answer.id,
                                        is_correct=answer.is_correct)
                                    )
               )
    return kb
