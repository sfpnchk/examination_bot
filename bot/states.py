from aiogram.dispatcher.filters.state import StatesGroup, State


class DisciplineState(StatesGroup):
    name = State()
    edit_name = State()
    short_description = State()
    edit_short_description = State()


class QuestionState(StatesGroup):
    photo = State()
    text = State()
    edit_text = State()
    edit_photo = State()

class AnswerState(StatesGroup):
    create = State()
    right_answer = State()
    wrong_answer = State()
    edit_text = State()


class UserMenuStepState(StatesGroup):
    chose_discipline = State()
    chose_action = State()

