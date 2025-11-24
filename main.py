import asyncio
import logging

from aiogram import Dispatcher

from src.bot.handlers.main_logic import router
from src.bot.handlers.start import start
from src.config import bot
from src.database.engine import create_db, session_maker
from src.get_kcal import get_kcal
from src.middleware.middleware import DataBaseSession

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Create .db file if not exist
    await create_db()
    # Checks for all 101 class is .db if not pars from USDA
    await get_kcal()
    logger.info("Starting Food Classifier Bot...")
    dp = Dispatcher()

    # Middleware for working async session
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.include_router(start)
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # asyncio.run(get_kcal())
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
