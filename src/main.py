import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, MenuButtonCommands

from src.bot.handlers import build_router
from src.bot.middlewares.notletters_client import NotlettersClientMiddleware
from src.config.settings import get_settings
from src.services.notletters_client import NotlettersClient


def setup_logging(level):
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def run_bot():
    settings = get_settings()
    setup_logging(settings.log_level)

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    await bot.set_my_commands([BotCommand(command="start", description="Меню")])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    async with NotlettersClient(
        api_key=settings.notletters_api_key,
        base_url=settings.notletters_api_base_url,
    ) as client:
        dp.update.outer_middleware(NotlettersClientMiddleware(client))
        dp.include_router(build_router())
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
