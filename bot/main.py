import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

# Импорт хендлеров и состояний
from bot.handlers.register import (
    start_register, set_role, set_enlist_date, choose_discharge, set_custom_discharge
)
from bot.handlers.status import status
from bot.states import RegisterStates

# Регистрация хендлеров
dp.register_message_handler(start_register, Command("start"), state="*")
dp.register_message_handler(set_role, state=RegisterStates.role)
dp.register_message_handler(set_enlist_date, state=RegisterStates.enlist_date)
dp.register_message_handler(choose_discharge, state=RegisterStates.discharge_choice)
dp.register_message_handler(set_custom_discharge, state=RegisterStates.discharge_custom)
dp.register_message_handler(status, commands=["status"], state="*")

# (Опционально) Хендлер помощи
@dp.message_handler(commands=["help"], state="*")
async def help_command(message: types.Message):
    await message.answer(
        "/start — регистрация или обновление данных\n"
        "/status — прогресс службы\n"
        "/help — помощь"
    )

# Запуск бота
if __name__ == "__main__":
    from aiogram import executor

    logging.info("Бот запущен. Ожидаем команды /start...")
    executor.start_polling(dp, skip_updates=True)
