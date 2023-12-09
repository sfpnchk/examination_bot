from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from bot.db.models import Discipline, Answer
from bot.enums import DisciplineActionEnum, QuestionActionEnum, AnswerActionEnum

discipline_callback = CallbackData("discipline", "action", "discipline_id")
discipline_edit_callback = CallbackData("discipline", "action", "discipline_id")
question_callback = CallbackData("question", "action", "discipline_id")
question_edit_callback = CallbackData("question", "action", "question_id")
answer_callback = CallbackData("answer", "action", "question_id")
answer_edit_callback = CallbackData("answer", "action", "answer_id")


admin_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        "Дисципліни",
        callback_data=discipline_callback.new(
            action=DisciplineActionEnum.view_sub_category.value, discipline_id=0,
        ),
    ),
)


def get_question_kb(question_id: int):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(
        "Детальніше",
            callback_data=question_edit_callback.new(
                action=QuestionActionEnum.detail.value,
                question_id=question_id)),
    )
    return kb


def create_question_kb(discipline_id: int):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        "Додати питання",
        callback_data=question_callback.new(
            action=QuestionActionEnum.create.value,
            discipline_id=discipline_id))
    )
    return kb


def edit_question_kb(question_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(
            "Додати правильну відповідь",
            callback_data=answer_callback.new(
                action=AnswerActionEnum.create_right_answer.value,
                question_id=question_id)),
            InlineKeyboardButton(
            "Додати неправильну відповідь",
            callback_data=answer_callback.new(
                action=AnswerActionEnum.create_wrong_answer.value,
                question_id=question_id)),
            InlineKeyboardButton(
            "Переглянути відповіді",
            callback_data=answer_callback.new(
                action=AnswerActionEnum.detail.value,
                question_id=question_id)),
            InlineKeyboardButton(
            "Редагувати фото питання",
            callback_data=question_edit_callback.new(
                action=QuestionActionEnum.edit_photo.value,
                question_id=question_id)),
        InlineKeyboardButton(
            "Редагувати текст питання",
            callback_data=question_edit_callback.new(
                action=QuestionActionEnum.edit_text.value,
                question_id=question_id)),
            InlineKeyboardButton(
            "Видалити питання",
            callback_data=question_edit_callback.new(
                action=QuestionActionEnum.delete.value,
                question_id=question_id)),
    )
    return kb


async def get_discipline_kb():
    disciplines = await Discipline.get_list()
    kb = InlineKeyboardMarkup()
    for discipline in disciplines:
        kb.row(InlineKeyboardButton(discipline.name,
                                    callback_data=discipline_callback.new(action=DisciplineActionEnum.detail.value,
                                                                        discipline_id=discipline.id)),
               InlineKeyboardButton("Видалити",
                                    callback_data=discipline_callback.new(action=DisciplineActionEnum.delete.value,
                                                                        discipline_id=discipline.id)),
               InlineKeyboardButton("Редагувати",
                                    callback_data=discipline_callback.new(action=DisciplineActionEnum.edit.value,
                                                                        discipline_id=discipline.id)))
    kb.add(InlineKeyboardButton("Додати дисципліну",
                                callback_data=discipline_callback.new(action=DisciplineActionEnum.create.value,
                                                                    discipline_id=0)))
    return kb


def edit_discipline_kb(discipline_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Редагувати назву",
                                callback_data=discipline_edit_callback.new(action=DisciplineActionEnum.edit_name.value,
                                                                         discipline_id=discipline_id)),
           InlineKeyboardButton("Редагувати корткий опис",
                                callback_data=discipline_edit_callback.new(action=DisciplineActionEnum.edit_short_description.value,
                                                                         discipline_id=discipline_id)),
    )
    return kb


def skip_photo_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Пропустити фото"))
    return kb


def get_answer_kb(answer_id: int):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("Видалити відповідь",
                                callback_data=answer_edit_callback.new(action=AnswerActionEnum.delete.value,
                                                                    answer_id=answer_id)),
           InlineKeyboardButton("Редагувати відповідь",
                                callback_data=answer_edit_callback.new(action=AnswerActionEnum.edit_text.value,
                                                                    answer_id=answer_id)),
        )
    return kb
