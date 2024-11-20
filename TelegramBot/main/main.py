import asyncio
import logging
from loguru import logger
from importlib import import_module
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # Импорт DefaultBotProperties
TOKEN = 'token'
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            module_name = f"cogs.{filename[:-3]}"
            try:
                module = import_module(module_name)
                router = getattr(module, "router", None)

                if router:
                    dp.include_router(router)
                    logger.info(f"Loaded extension: {module_name}")
                else:
                    logger.error(f"{module_name} does not have 'router'.")
            except Exception as e:
                logger.error(f"Failed to load {module_name}: {e}")
async def main():
    try:
        logger.info("Starting bot...")
        await load_extensions()
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())


