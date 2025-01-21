from aiogram.fsm.state import State, StatesGroup


class PhoneNumber(StatesGroup):
    number = State()