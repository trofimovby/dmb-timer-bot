from aiogram import Bot, Dispatcher, executor, types
from bot.config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я — твой личный DMB-бот. Готов помочь отсчитывать дни до дембеля.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
