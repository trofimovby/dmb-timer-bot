from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def subscription_modes_kb(current_mode: str | None):
    buttons = [
        InlineKeyboardButton("📖 Ежедневно", callback_data="set_notify_daily"),
        InlineKeyboardButton("🗓 Раз в неделю", callback_data="set_notify_weekly"),
        InlineKeyboardButton("📆 Ключевые даты", callback_data="set_notify_milestones"),
        InlineKeyboardButton("❌ Отключить", callback_data="set_notify_off"),
    ]

    kb = InlineKeyboardMarkup(row_width=1)
    for btn in buttons:
        if current_mode and btn.callback_data.endswith(current_mode):
            btn.text += " ✅"
        kb.add(btn)
    return kb
