#!/usr/bin/env python3
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI
import uvicorn

import config
from adapters.inbound.http.api.router import api_router
from adapters.inbound.http.telegram.handlers import router as tg_router
from adapters.outbound.postgres.database import init_db

app = FastAPI(
    title="Book Recommendation API",
    description="Semantic book recommendation system with Telegram bot interface",
    version="1.0.0",
)
app.include_router(api_router)


@app.on_event("startup")
def startup():
    init_db()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logger = logging.getLogger(__name__)

    init_db()
    logger.info("✅ Database initialized")

    dp: Dispatcher | None = None
    bot: Bot | None = None
    if config.TELEGRAM_BOT_TOKEN:
        bot = Bot(
            token=config.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        dp = Dispatcher()
        dp.include_router(tg_router)
        logger.info("✅ Telegram bot configured")
    else:
        logger.warning(
            "⚠️ TELEGRAM_BOT_TOKEN is not set; starting API only (no bot polling)."
        )

    uvi_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(uvi_config)
    logger.info("✅ FastAPI server configured")

    logger.info("🚀 Starting API server (http://0.0.0.0:8000)...")
    if config.TELEGRAM_BOT_TOKEN:
        logger.info("📚 Bot: @knigovoodbot")
    logger.info("📖 API Docs: http://localhost:8000/docs")

    tasks = [server.serve()]
    if dp is not None and bot is not None:
        tasks.append(
            dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
