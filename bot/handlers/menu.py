from aiogram import types
from datetime import date, datetime

from bot.database.db import SessionLocal
from bot.database.models import User
from bot.keyboards.subscribe_kb import subscription_modes_kb
from services.notifier import get_quote


# === Обработчик кнопочного меню ===
async def handle_menu_choice(message: types.Message):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()

        if not user:
            await message.answer("Сначала пройдите регистрацию через /start.")
            return

        if message.text == "📊 Мой статус":
            await send_status(message, user)

        elif message.text == "🔔 Подписка":
            keyboard = subscription_modes_kb(user.notify_mode)
            await message.answer("Выберите режим напоминаний:", reply_markup=keyboard)

        elif message.text == "💬 Чат поддержки":
            await message.answer(
                "Присоединяйся к нашему чату! Здесь можно задать вопрос или поделиться опытом:\n\n"
                "👉 https://t.me/+oW2QxTdb56tjYTQy"
            )

    finally:
        session.close()


# === Отправка статуса пользователю ===
async def send_status(message: types.Message, user: User):
    enlist = user.enlist_date.strftime('%d.%m.%Y')
    discharge = user.discharge_date.strftime('%d.%m.%Y')
    today = date.today()

    total_days = (user.discharge_date - user.enlist_date).days
    passed_days = (today - user.enlist_date).days
    remaining_days = (user.discharge_date - today).days
    percent = (passed_days / total_days * 100) if total_days > 0 else 0

    # Прогресс-бар
    bar_length = 20
    filled = round(bar_length * percent / 100)
    empty = bar_length - filled
    progress_bar = "▮" * filled + "▯" * empty

    # Статус подписки
    notify_status = {
        None: "❌ Выключены",
        "daily": "📖 Ежедневные",
        "weekly": "🗓 Раз в неделю",
        "milestones": "📆 Только ключевые даты"
    }.get(user.notify_mode, "❔ Неизвестно")

    # Цитата
    role_key = "serve" if user.role == "Я служу" else "wait"
    try:
        quote = get_quote(remaining_days, role_key, datetime.today(), total_days)
        quote_line = f"\n\n🧠 <i>{quote}</i>" if quote else ""
    except Exception:
        quote_line = ""

    text = (
        f"🪖 <b>Роль:</b> {user.role}\n"
        f"📅 <b>Призыв:</b> {enlist}\n"
        f"🎖 <b>Дембель:</b> {discharge}\n\n"
        f"⏳ <b>Прошло:</b> {passed_days} дн.\n"
        f"🧭 <b>Осталось:</b> {remaining_days} дн.\n"
        f"📊 <b>Прогресс:</b> {percent:.2f}%\n"
        f"{progress_bar}\n\n"
        f"🔔 <b>Напоминания:</b> {notify_status}"
        f"{quote_line}"
    )

    await message.answer(text, parse_mode="HTML")


# === Обработка inline-кнопок подписки ===
async def handle_notify_callback(call: types.CallbackQuery):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=call.from_user.id).first()

        mapping = {
            "set_notify_daily": "daily",
            "set_notify_weekly": "weekly",
            "set_notify_milestones": "milestones",
            "set_notify_off": None
        }

        mode = mapping.get(call.data)
        user.notify_mode = mode
        session.commit()

        name_map = {
            "daily": "📖 Ежедневные",
            "weekly": "🗓 Раз в неделю",
            "milestones": "📆 Только ключевые даты",
            None: "❌ Выключены"
        }

        await call.answer("Настройки обновлены.")
        await call.message.edit_text(f"🔔 Напоминания: {name_map[mode]}")

    finally:
        session.close()
