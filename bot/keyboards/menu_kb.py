from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📊 Мой статус"),
        KeyboardButton("🔔 Подписка")
    )
    kb.add(
        KeyboardButton("✍️ Обновить данные"),
        KeyboardButton("💬 Чат поддержки")  # новая кнопка
    )
    return kb
