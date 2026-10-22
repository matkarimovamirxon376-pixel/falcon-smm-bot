"""FALCON SMM Telegram bot — kirish nuqtasi (entry point).

Ishga tushirish:
    1. .env.example dan .env yarating va TOKEN/API kalitni to'ldiring
    2. pip install -r requirements.txt
    3. python bot.py
"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import load_config
from app.falcon_api import FalconAPI
from app.handlers import setup_routers
from app.middleware import DependenciesMiddleware
from app.storage import OrderStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("falcon-bot")


async def main() -> None:
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Umumiy obyektlar
    api = FalconAPI(api_url=config.api_url, api_key=config.api_key)
    order_storage = OrderStorage()

    # Middleware — har bir handlerga `api` va `storage` ni uzatadi
    deps = DependenciesMiddleware(api=api, storage=order_storage)
    dp.message.middleware(deps)
    dp.callback_query.middleware(deps)

    # Routerlar
    dp.include_router(setup_routers())

    logger.info("🦅 FALCON SMM bot ishga tushdi...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
