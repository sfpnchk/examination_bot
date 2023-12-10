from aiogram.dispatcher.filters import BoundFilter
from aiogram.types.message import Message

from bot.utils import Config


class IsSuperAdmin(BoundFilter):
    async def check(self, msg: Message) -> bool:
        user_id = msg.from_user.id
        if user_id not in Config.get_config()["admins"]:
            await msg.answer("Тільки для адміністраторів")
            return False
        return True
