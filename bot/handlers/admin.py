from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.orm import Session
from datetime import date
from bot.database import get_session
from bot.models import User

# Telegram ID администраторов (лучше загрузить из переменной окружения)
import os
ADMINS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

async def admin_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    with get_session() as session:
        total = session.query(User).count()
        soldiers = session.query(User).filter(User.role == "soldier").count()
        supporters = session.query(User).filter(User.role == "supporter").count()
        subscribed = session.query(User).filter(User.is_subscribed == True).count()
        unsubscribed = total - subscribed

        upcoming = (
            session.query(User)
            .filter(User.discharge_date >= date.today())
            .order_by(User.discharge_date)
            .limit(3)
            .all()
        )

    text = (
        f"👥 Пользователи: {total}\n"
        f"🪖 Служащие: {soldiers} | 🎗 Товарищи: {supporters}\n"
        f"📣 Подписаны: {subscribed} | 🚫 Без подписки: {unsubscribed}\n"
        f"📆 Ближайшие дембеля:\n"
    )

    if upcoming:
        for u in upcoming:
            text += f"— {u.discharge_date.strftime('%d.%m.%Y')} (id: {u.telegram_id})\n"
    else:
        text += "— нет данных"

    await message.answer(text)

async def admin_broadcast(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    text = message.text.replace("/admin_broadcast", "", 1).strip()
    if not text:
        await message.answer("⚠️ Укажи текст рассылки после команды.")
        return

    bot = message.bot  # получаем бота из контекста сообщения

    sent = 0
    failed = 0

    with get_session() as session:
        users = session.query(User).filter(User.is_subscribed == True).all()

    for user in users:
        try:
            await bot.send_message(user.telegram_id, text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Разослано: {sent}\n❌ Ошибок: {failed}")

def register_admin_handlers(dp):
    dp.register_message_handler(admin_stats, commands=["admin", "admin_stats"])
    dp.register_message_handler(admin_broadcast, commands=["admin_broadcast"])
