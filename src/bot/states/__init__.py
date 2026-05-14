from aiogram.fsm.state import State, StatesGroup


class AddAccount(StatesGroup):
    waiting_input = State()
