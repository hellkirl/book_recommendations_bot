import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import config
from adapters.outbound.postgres.database import init_db
from .handlers import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    init_db()

    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Bot starting...")
    await dp.start_polling(bot)


def run_bot() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
