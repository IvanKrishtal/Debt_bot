import asyncio
from dispatcher import bot
from aiogram.client.session.aiohttp import AiohttpSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, PROXY_URL
from dispatcher import dp
from handlers import remind_command
import handlers


async def main():
    print("🚀 Бот запущен")

    # ? Создает планировщика, отправляющего сообщения в 16:00 и 20:00
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remind_command, "cron", hour=16, minute=0)
    scheduler.add_job(remind_command, "cron", hour=20, minute=0)
    scheduler.start()

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        print("👋 Бот выключен.")
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
