import logging
from aiogram import types
from datetime import date

from bot.database.db import SessionLocal
from bot.models import User

logger = logging.getLogger(__name__)

def get_progress_bar(percent: float, length: int = 20) -> str:
    filled_length = int(length * percent)
    bar = '▇' * filled_length + '░' * (length - filled_length)
    return f"{bar} {percent * 100:.1f}%"

async def status(message: types.Message):
    telegram_id = message.from_user.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            await message.answer("Вы ещё не зарегистрированы. Используйте команду /start.")
            return

        today = date.today()
        total_days = (user.discharge_date - user.enlist_date).days
        passed_days = (today - user.enlist_date).days
        remaining_days = (user.discharge_date - today).days

        if passed_days < 0:
            await message.answer("Служба ещё не началась.")
            return

        if remaining_days < 0:
            await message.answer("Поздравляем, вы уже демобилизовались! 🎉")
            return

        progress = passed_days / total_days if total_days else 0
        bar = get_progress_bar(progress)

        await message.answer(
            f"🪖 Призыв: {user.enlist_date.strftime('%d.%m.%Y')}\n"
            f"🎖 Дембель: {user.discharge_date.strftime('%d.%m.%Y')}\n\n"
            f"⏳ Прошло: {passed_days} дней\n"
            f"📅 Осталось: {remaining_days} дней\n"
            f"{bar}"
        )

    except Exception as e:
        logger.exception("Ошибка при расчёте статуса службы")
        await message.answer("Произошла ошибка. Попробуйте позже.")
    finally:
        session.close()
