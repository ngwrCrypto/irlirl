import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_ID
from db.manager import db
from handlers import common, expenses, daily
from jobs.scheduler import setup_scheduler

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Initialize DB
    await db.create_tables()

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Send Startup Message
    await bot.send_message(ADMIN_ID, "Бот запущено дороу! 🚀")

    # Register Routers
    dp.include_router(common.router)
    dp.include_router(expenses.router)
    dp.include_router(daily.router)

    # Setup Scheduler
    setup_scheduler(bot)

    # Start Polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
