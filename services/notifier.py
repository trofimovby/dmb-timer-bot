import json
import logging
import re
from datetime import datetime
from pathlib import Path
from aiogram import Bot

from bot.database.models import User
from bot.database.db import SessionLocal

logger = logging.getLogger(__name__)

# === Загрузка цитат ===
QUOTES_PATH = Path(__file__).parent.parent / "data" / "quotes.json"

try:
    with open(QUOTES_PATH, encoding="utf-8") as f:
        QUOTES = json.load(f)
except Exception as e:
    logger.critical(f"Не удалось загрузить файл цитат: {e}")
    QUOTES = {}

# === Получение подходящей цитаты ===
def get_quote(days_left: int, role: str, today: datetime, total_days: int) -> str:
    date_str = today.strftime("%d.%m")

    # Праздничная дата
    if date_str in QUOTES.get("holidays", {}):
        raw = QUOTES["holidays"][date_str].get(role, "")
    # Круглая дата
    elif str(days_left) in QUOTES.get("milestones", {}).get(role, {}):
        raw = QUOTES["milestones"][role][str(days_left)]
    else:
        daily = QUOTES.get("daily", {}).get(role)
        if not daily:
            return ""

        if isinstance(daily, dict):
            raw = daily.get(str(total_days - days_left), "")
        elif isinstance(daily, list):
            index = (total_days - days_left) % len(daily)
            raw = daily[index]
        else:
            return ""

    # Удаляем префиксы SERVE | или WAIT |
    return re.sub(r"^(SERVE|WAIT)\s*\|\s*", "", raw)

# === Рассылка всем подписанным ===
async def send_daily_notifications(bot: Bot):
    session = SessionLocal()
    today = datetime.today().date()

    users = session.query(User).filter(User.notify_mode.isnot(None)).all()

    for user in users:
        if not user.enlist_date or not user.discharge_date:
            continue

        total_days = (user.discharge_date - user.enlist_date).days
        passed_days = (today - user.enlist_date).days
        days_left = (user.discharge_date - today).days

        if days_left < 0 or passed_days < 0 or total_days <= 0:
            continue

        # Пропуск по режиму подписки
        if user.notify_mode == "milestones" and str(days_left) not in QUOTES.get("milestones", {}).get("serve", {}):
            continue
        if user.notify_mode == "weekly" and today.weekday() != 0:  # только по понедельникам
            continue

        try:
            role_key = "serve" if user.role == "Я служу" else "wait"
            quote = get_quote(days_left, role_key, datetime.today(), total_days)
            text = f"📅 Осталось {days_left} дней до дембеля!\n\n💬 {quote}"
            await bot.send_message(user.telegram_id, text)
        except Exception as e:
            logger.exception(f"Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}")

    session.close()

# === Отправка тестового уведомления ===
async def send_test_notification(bot: Bot, telegram_id: int):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if not user or not user.enlist_date or not user.discharge_date:
        await bot.send_message(telegram_id, "Сначала необходимо пройти регистрацию.")
        return

    total_days = (user.discharge_date - user.enlist_date).days
    today = datetime.today().date()
    days_left = (user.discharge_date - today).days

    if total_days <= 0 or days_left < 0:
        await bot.send_message(telegram_id, "Срок службы некорректен.")
        return

    role_key = "serve" if user.role == "Я служу" else "wait"
    quote = get_quote(days_left, role_key, datetime.today(), total_days)

    text = f"📅 Осталось {days_left} дней до дембеля!\n\n💬 {quote}"
    await bot.send_message(telegram_id, text)

    session.close()
