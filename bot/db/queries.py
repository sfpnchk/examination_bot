from typing import Optional

from sqlalchemy import select, func

from bot.db.models import Question


async def get_random_question(session, discipline_id: int) -> Optional[Question]:
    query = (
        select(Question).select_from(Question).filter_by(discipline_id=discipline_id)
        .order_by(func.random())
        .limit(1)
    )
    row = await session.execute(query)
    return row.scalars().one_or_none()
