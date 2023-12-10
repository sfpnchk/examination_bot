from bot.core import bot
from bot.db.queries import get_question
from aiogram import types

from bot.kb.user_kb import get_answers


async def send_question(session, discipline_id, user_id):
    question = await get_question(
        session, discipline_id=int(discipline_id), user_id=user_id
    )
    if question.photo:
        media = types.MediaGroup()
        for photo_id in question.photo:
            media.attach_photo(photo_id)

        await bot.send_media_group(chat_id=user_id, media=media)
    await bot.send_message(chat_id=user_id, text=question.text, reply_markup=await get_answers(question.id))
