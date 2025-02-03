from aiogram.fsm.state import State, StatesGroup


class User(StatesGroup):
    number = State()
    category = State()
    location = State()