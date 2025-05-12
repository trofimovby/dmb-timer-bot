from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterStates(StatesGroup):
    role = State()           # кто служит
    enlist_date = State()    # дата призыва
    discharge_choice = State()  # выбор шаблона или ручной ввод
    discharge_custom = State()  # если пользователь вводит вручную
