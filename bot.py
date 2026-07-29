import asyncio
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN, PROXY_URL
from dispatcher import dp
import handlers

session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=BOT_TOKEN, session=session)


async def main():
    print("🚀 Бот запущен")
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        print("👋 Бот выключен.")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
