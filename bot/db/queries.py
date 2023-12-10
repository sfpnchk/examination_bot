from typing import Optional

from sqlalchemy import select, func, and_, literal_column
from sqlalchemy.orm import aliased

from bot.db.models import Question, Discipline, UserAnswer, Answer
from bot.types import UserDisciplineStatistics


async def get_question(session, discipline_id: int, user_id) -> Optional[Question]:
    # check last tries
    last_user_tries_query = (
        select(
            Answer.is_correct
        )
        .select_from(Answer)
        .join(UserAnswer, UserAnswer.answer_id == Answer.id)
        .join(Question, Question.id == Answer.question_id)
        .where(UserAnswer.user_id == user_id, Question.discipline_id == discipline_id)
        .order_by(UserAnswer.created_at.desc())
        .limit(3)
    )
    last_user_tries = (await session.execute(last_user_tries_query)).scalars().all()
    if len(last_user_tries) < 3:
        query = (
            select(Question)
            .select_from(Question)
            .filter_by(discipline_id=discipline_id)
            .order_by(func.random())
            .limit(1)
        )
        row = await session.execute(query)
        return row.scalars().one_or_none()

    correct_answer: UserAnswer = aliased(UserAnswer, name="correct_answer")
    un_correct_answer: UserAnswer = aliased(UserAnswer, name="un_correct_answer")
    filters = [
        UserAnswer.user_id == user_id,
        Discipline.id == discipline_id,
    ]

    query = (
        select(
            Question,

        ).filter(*filters)
        .select_from(Question)
        .join(Answer, Answer.question_id == Question.id)
        .join(
            correct_answer,
            and_(correct_answer.answer_id == Answer.id, Answer.is_correct.is_(True)),
            isouter=True,
        )
        .join(
            un_correct_answer,
            and_(
                un_correct_answer.answer_id == Answer.id, Answer.is_correct.is_(False)
            ),
            isouter=True,
        ).group_by(Question.id).limit(1).order_by(func.random())
    )

    correct_answer_of_last_tries = sum(
        [answer for answer in last_user_tries if answer is True]
    )

    if correct_answer_of_last_tries == 0:
        query = query.having(((100 * func.greatest(1, func.count(correct_answer.id))) / func.greatest(1, (
                func.count(correct_answer.id) + func.count(un_correct_answer.id)))) <= 70)
    else:
        query = query.having(((100 * func.greatest(1, func.count(correct_answer.id))) / func.greatest(1, (
                func.count(correct_answer.id) + func.count(un_correct_answer.id)))) > 70)

    question = (await session.execute(query)).scalars().one_or_none()
    if  question is None:
        query = (
            select(Question)
            .select_from(Question)
            .filter_by(discipline_id=discipline_id)
            .order_by(func.random())
            .limit(1)
        )
        row = await session.execute(query)
        return row.scalars().one_or_none()
    return question


async def get_user_active_disciplines(session, user_id):
    query = (
        select(Discipline)
        .select_from(Discipline)
        .join(Question, Question.discipline_id == Discipline.id)
        .join(Answer, Answer.question_id == Question.id)
        .join(UserAnswer, UserAnswer.answer_id == Answer.id)
        .where(UserAnswer.user_id == user_id)
    ).group_by(
        Discipline.id,
        Discipline.name,
        Discipline.created_at,
        Discipline.short_description,
    )

    row = await session.execute(query)
    return row.scalars().all()


async def get_user_stats_for_discipline(session, user_id: int, discipline_id: int):
    # кількість правильних відповідей всередині дисципліни від юзера (2 однакові правильні відповіді на 1 питання рахуються як 2)
    right_answers_count_query = (
        select(func.count(UserAnswer.id))
        .select_from(UserAnswer)
        .join(Answer, UserAnswer.answer_id == Answer.id)
        .join(Question, Question.id == Answer.question_id)
        .join(Discipline, Discipline.id == Question.discipline_id)
        .where(
            UserAnswer.user_id == user_id,
            Discipline.id == discipline_id,
            Answer.is_correct.is_(True),
        )
    )
    right_answers_count = (
        (await session.execute(right_answers_count_query)).scalars().one()
    )

    # кількість всіх відповідей юзера всередині дисципліни
    all_answers_count_query = (
        select(func.count(UserAnswer.id))
        .select_from(UserAnswer)
        .join(Answer, UserAnswer.answer_id == Answer.id)
        .join(Question, Question.id == Answer.question_id)
        .join(Discipline, Discipline.id == Question.discipline_id)
        .where(UserAnswer.user_id == user_id, Discipline.id == discipline_id)
    )
    all_answers_count = (await session.execute(all_answers_count_query)).scalars().one()

    # кількість правильно пройдених питань юзера всередині дисципліни (2 однакові правильні відповіді на 1 питання рахуються як 1 )
    distinct_right_answers_count_query = (
        select(func.count(func.distinct(Question.id)))
        .select_from(UserAnswer)
        .join(Answer, UserAnswer.answer_id == Answer.id)
        .join(Question, Question.id == Answer.question_id)
        .join(Discipline, Discipline.id == Question.discipline_id)
        .where(
            UserAnswer.user_id == user_id,
            Discipline.id == discipline_id,
            Answer.is_correct.is_(True),
        )
        .group_by(Question.id)
    )
    distinct_right_answers_count = (
        (await session.execute(distinct_right_answers_count_query)).scalars().one()
    )

    # кількість питань всередині дисципліни
    discipline_questions_count_query = (
        select(func.count(Question.id))
        .select_from(Question)
        .join(Discipline, Question.discipline_id == Discipline.id)
        .where(Discipline.id == discipline_id)
    )
    discipline_questions_count = (
        (await session.execute(discipline_questions_count_query)).scalars().one()
    )

    return UserDisciplineStatistics(
        discipline_question_count=discipline_questions_count,
        discipline_right_answer_count=distinct_right_answers_count,
        user_all_answers_count=all_answers_count,
        user_right_answers_count=right_answers_count,
    )
