import enum


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        """https://docs.python.org/3/library/enum.html#using-automatic-values"""
        return name


class DisciplineActionEnum(AutoName):
    create = enum.auto()
    detail = enum.auto()
    delete = enum.auto()
    edit = enum.auto()
    edit_name = enum.auto()
    edit_short_description = enum.auto()
    view_sub_category = enum.auto()
    view_list = enum.auto()


class QuestionActionEnum(AutoName):
    create = enum.auto()
    detail = enum.auto()
    delete = enum.auto()
    edit_photo = enum.auto()
    edit_text = enum.auto()
    view = enum.auto()


class AnswerActionEnum(AutoName):
    create_right_answer = enum.auto()
    create_wrong_answer = enum.auto()
    detail = enum.auto()
    delete = enum.auto()
    edit_text = enum.auto()
    show_answer = enum.auto()
