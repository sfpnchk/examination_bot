from dataclasses import dataclass


@dataclass(frozen=True)
class UserDisciplineStatistics:
    discipline_question_count: int
    discipline_right_answer_count: int
    user_right_answers_count: int
    user_all_answers_count: int

    @property
    def right_answers_percent(self):
        return self.user_right_answers_count * 100 / self.user_all_answers_count
