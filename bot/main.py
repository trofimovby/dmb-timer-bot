import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import aiocron

from services.notifier import send_daily_notifications, send_test_notification
from bot.handlers.register import (
    start_register, set_role, set_enlist_date, choose_discharge, set_custom_discharge
)
from bot.handlers.menu import handle_menu_choice, handle_notify_callback
from bot.states import RegisterStates

# === Настройка логгирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# === Загрузка окружения ===
load_dotenv()

# === Инициализация бота ===
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
bot["dispatcher"] = dp

# === Админка ===
from bot.handlers.admin import register_admin_handlers
register_admin_handlers(dp)


# === FSM регистрация ===
dp.register_message_handler(set_role, state=RegisterStates.role)
dp.register_message_handler(set_enlist_date, state=RegisterStates.enlist_date)
dp.register_message_handler(choose_discharge, state=RegisterStates.discharge_choice)
dp.register_message_handler(set_custom_discharge, state=RegisterStates.discharge_custom)

# === Команды ===
@dp.message_handler(commands=["start"], state="*")
async def handle_start(message: types.Message, state: FSMContext):
    await start_register(message, state)

@dp.message_handler(commands=["help"], state="*")
async def handle_help(message: types.Message):
    await message.answer(
        "🤖 Возможности бота:\n"
        "• /start — регистрация или обновление данных\n"
        "• 📋 Меню — кнопки статуса и подписки\n"
        "• /test_notify — прислать пример напоминания\n"
        "• /help — справка"
    )

@dp.message_handler(commands=["test_notify"], state="*")
async def handle_test_notify(message: types.Message):
    await send_test_notification(bot, message.from_user.id)

# === Обновление данных ===
@dp.message_handler(lambda msg: msg.text == "✍️ Обновить данные", state="*")
async def handle_update_data(message: types.Message, state: FSMContext):
    await start_register(message, state)

# === Callback-кнопки (настройки подписки) ===
dp.register_callback_query_handler(handle_notify_callback, lambda c: c.data.startswith("set_notify_"))

# === Главное меню ===
dp.register_message_handler(handle_menu_choice, state="*")

# === Фоновая задача: ежедневная рассылка в 09:00 ===
@aiocron.crontab("0 9 * * *")
async def daily_job():
    await send_daily_notifications(bot)

# === Запуск бота ===
if __name__ == "__main__":
    from aiogram import executor
    logging.info("Бот запущен. Ожидаем команду /start...")
    executor.start_polling(dp, skip_updates=True)
