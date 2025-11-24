from aiogram.fsm.state import StatesGroup, State


class RegStates(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()
    ready = State()


class PhotoStates(StatesGroup):
    waiting_photo = State()
    confirm_prediction = State()
    waiting_grams = State()
    confirm_name = State()
    ask_calories = State()
