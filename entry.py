import argparse
import logging
import sys

from aiogram import Dispatcher
from aiogram.utils import executor
from setproctitle import setproctitle, getproctitle

from bot.core import create_dp
from bot.db.base import db_connect
from bot.utils import Config

parser = argparse.ArgumentParser(
    description="Tea Bot",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(
    "-c",
    "--config",
    dest="config_file",
    help="path to configuration file",
)
parser.add_argument("--run", action="store_true", help="Run bot")
parser.add_argument("--migrate", action="store_true", help="Migrate database")
parser.add_argument(
    "--revision", action="store_true", help="Create new migration revision"
)
parser.add_argument("--downgrade", action="store_true", help="Downgrade database")

args = parser.parse_args()
config = Config.load_config(args.config_file or "local.yaml")
logger = logging.getLogger("entry")
if args.migrate:
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrate database")
    sys.exit(0)

if args.revision:
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", config["database_uri"])
    message = input("Comment revision: ")
    command.revision(alembic_cfg, message, autogenerate=True)
    logger.info("Create database migration")
    sys.exit(0)

if args.downgrade:
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    revision = input("Downgrade revision (-1 for previous, Enter to skip): ")
    if revision:
        logger.info(f"Downgrade database to revision {revision}")
        command.downgrade(alembic_cfg, revision)
    else:
        logger.info("Downgrade skipped.")
    sys.exit(0)


async def on_startup(dp: Dispatcher):
    from bot import handlers  # noqa

    await db_connect(config["database_uri"])


async def on_shutdown(dp: Dispatcher) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()


if args.run:
    setproctitle(f"{getproctitle()} - {parser.description}")
    dp = create_dp(config)
    executor.start_polling(
        dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
    )
