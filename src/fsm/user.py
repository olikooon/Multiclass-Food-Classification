from aiogram.fsm.state import StatesGroup, State


# State for registration
class RegStates(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()
    ready = State()


# State for photo load
class PhotoStates(StatesGroup):
    waiting_photo = State()
    confirm_prediction = State()
    waiting_grams = State()
    confirm_name = State()
    ask_calories = State()
