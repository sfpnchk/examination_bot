from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode

from bot.middlewares import AlbumMiddleware

dp: Dispatcher
bot: Bot


def create_dp(config: dict):
    global dp, bot
    bot = Bot(config["bot_token"], parse_mode=ParseMode.HTML, validate_token=True)
    storage = RedisStorage2()
    dp = Dispatcher(bot, storage=storage)

    dp.setup_middleware(AlbumMiddleware())

    return dp
