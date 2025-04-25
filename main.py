import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import common_router, registration_router, faq_router, questions_router, chat_router
from utils.file_operations import setup_sample_faq
from utils.middleware import LanguageTrackingMiddleware
from utils.logger import log_info, log_error


# Создание бота и dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация middleware
dp.message.middleware(LanguageTrackingMiddleware())
dp.callback_query.middleware(LanguageTrackingMiddleware())

# Регистрация роутеров
dp.include_router(common_router)
dp.include_router(registration_router)
dp.include_router(faq_router)
dp.include_router(questions_router)
dp.include_router(chat_router)


async def main():
    """Старт бота."""
    # Создание необходимых каталогов
    os.makedirs("data", exist_ok=True)
    os.makedirs("questions", exist_ok=True)
    os.makedirs("faq", exist_ok=True)

    # Установка образца FAQ
    await setup_sample_faq()

    try:
        # Запуск Бота
        log_info("Бот запущен и готов к работе")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        log_info("Бот остановлен")
    except Exception as e:
        log_error(f"Произошла ошибка при запуске бота: {e}")
    finally:
        # Закрытие сессии бота
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("Бот остановлен пользователем")
    except Exception as e:
        log_error(f"Необработанная ошибка: {e}")
