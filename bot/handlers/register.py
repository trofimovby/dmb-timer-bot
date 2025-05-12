import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.keyboards.register_kb import role_kb, discharge_kb
from bot.states import RegisterStates
from bot.database.models import User
from bot.database.db import SessionLocal

logger = logging.getLogger(__name__)

# === Шаг 1. Старт регистрации ===
async def start_register(message: types.Message, state: FSMContext):
    session = SessionLocal()
    telegram_id = message.from_user.id
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).one_or_none()

        if user:
            text = (
                f"Вы уже зарегистрированы.\n\n"
                f"🪖 Роль: {user.role}\n"
                f"📅 Призыв: {user.enlist_date.strftime('%d.%m.%Y')}\n"
                f"🎖 Дембель: {user.discharge_date.strftime('%d.%m.%Y')}\n\n"
                f"Вы хотите обновить эти данные?"
            )
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("🔄 Обновить", "❌ Отмена")
            await message.answer(text, reply_markup=keyboard)
            await RegisterStates.role.set()
        else:
            await message.answer("Кто проходит службу?", reply_markup=role_kb())
            await RegisterStates.role.set()
    finally:
        session.close()

# === Шаг 2. Выбор роли ===
async def set_role(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Регистрация отменена.", reply_markup=types.ReplyKeyboardRemove())
        return

    if message.text == "🔄 Обновить":
        await message.answer("Кто проходит службу?", reply_markup=role_kb())
        return  # оставляем состояние RegisterStates.role

    await state.update_data(role=message.text)
    await message.answer("Введите дату призыва в формате дд.мм.гггг", reply_markup=types.ReplyKeyboardRemove())
    await RegisterStates.enlist_date.set()

# === Шаг 3. Ввод даты призыва ===
async def set_enlist_date(message: types.Message, state: FSMContext):
    try:
        enlist_date = datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(enlist_date=enlist_date)
        await message.answer("Когда дембель?", reply_markup=discharge_kb())
        await RegisterStates.discharge_choice.set()
    except ValueError:
        logger.warning(f"Неверный формат даты призыва: {message.text}")
        await message.answer("Формат неверен. Пример: 25.06.2024")

# === Шаг 4. Выбор срока службы ===
async def choose_discharge(message: types.Message, state: FSMContext):
    data = await state.get_data()
    enlist_date = data.get("enlist_date")

    discharge_map = {
        "📆 6 месяцев": timedelta(days=183),
        "📆 1 год": timedelta(days=365),
        "📆 1.5 года": timedelta(days=547),
    }

    if message.text in discharge_map:
        discharge_date = enlist_date + discharge_map[message.text]
        await save_user(message, state, discharge_date)
    elif message.text == "✍️ Свой вариант":
        await message.answer("Введите дату дембеля в формате дд.мм.гггг")
        await RegisterStates.discharge_custom.set()
    else:
        logger.info(f"Неизвестный вариант дембеля: {message.text}")
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

# === Шаг 5. Пользователь вводит свою дату дембеля ===
async def set_custom_discharge(message: types.Message, state: FSMContext):
    try:
        discharge_date = datetime.strptime(message.text, "%d.%m.%Y")
        await save_user(message, state, discharge_date)
    except ValueError:
        logger.warning(f"Неверный формат даты дембеля: {message.text}")
        await message.answer("Формат неверен. Пример: 25.06.2025")

# === Финальный шаг. Сохранение данных в БД ===
async def save_user(message: types.Message, state: FSMContext, discharge_date: datetime):
    data = await state.get_data()
    telegram_id = message.from_user.id

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).one_or_none()

        if user:
            user.role = data["role"]
            user.enlist_date = data["enlist_date"]
            user.discharge_date = discharge_date
            logger.info(f"Обновлены данные пользователя {telegram_id}")
        else:
            user = User(
                telegram_id=telegram_id,
                role=data["role"],
                enlist_date=data["enlist_date"],
                discharge_date=discharge_date
            )
            session.add(user)
            logger.info(f"Добавлен новый пользователь {telegram_id}")

        session.commit()
        await message.answer(f"Дембель назначен на: {discharge_date.strftime('%d.%m.%Y')}")
        await state.finish()

    except Exception:
        session.rollback()
        logger.exception(f"Ошибка при сохранении пользователя {telegram_id}")
        await message.answer("Произошла ошибка при сохранении. Попробуйте позже.")
    finally:
        session.close()
