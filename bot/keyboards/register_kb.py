from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def role_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Я служу"), KeyboardButton("Товарищ служит"))
    return kb

def discharge_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📆 6 месяцев"),
        KeyboardButton("📆 1 год"),
        KeyboardButton("📆 1.5 года")
    )
    kb.add(KeyboardButton("✍️ Свой вариант"))
    return kb
