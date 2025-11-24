import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot import keyboard as kb
from src.config import bot
from src.database.query import get_user, add_user
from src.fsm.user import RegStates

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

start = Router()


@start.message(CommandStart())
async def cmd_start(msg: Message, session: AsyncSession, state: FSMContext):
    welcome_text = """
<b>Welcome to Food Classifier Bot!</b>

I can recognize dishes using the Food-101 dataset. Just send me a photo of the food, and I'll tell you what it is!

<em>101 food categories are supported, including pizza, sushi, burgers, and more!</em>

But you need to register first. Please indicate gender (m/f):

    """
    user = await get_user(session, msg.from_user.id)
    if user:
        await msg.answer(
            "<b>Welcome to Food Classifier Bot!</b>\n You're already registered. "
            "Use /add to add food or /profile to view your profile.", parse_mode=ParseMode.HTML)
        return
    await msg.answer(welcome_text, parse_mode=ParseMode.HTML)
    await state.set_state(RegStates.gender)


# Full logic of registration
@start.message(RegStates.gender)
async def validate_gender(msg: Message, state: FSMContext):
    gender = msg.text.strip().lower()
    if gender not in ('m', 'f', 'male', 'female'):
        await msg.answer("Please enter 'm' or 'f'.")
        return
    await state.update_data(gender=gender)
    await msg.answer("Your full age:")
    await state.set_state(RegStates.age)


@start.message(RegStates.age)
async def validate_age(msg: Message, state: FSMContext):
    try:
        age = int(msg.text.strip())
        await state.update_data(age=age)
        await msg.answer("Your height in centimeters:")
        await state.set_state(RegStates.height)
    except ValueError:
        await msg.answer("Please enter a valid number for age (e.g. 20).")


@start.message(RegStates.height)
async def validate_height(msg: Message, state: FSMContext):
    try:
        h = float(msg.text.strip())
        await state.update_data(height=h)
        await msg.answer("Your weight in kilograms:")
        await state.set_state(RegStates.weight)
    except ValueError:
        await msg.answer("Please enter a valid number for height (e.g. 175).")


@start.message(RegStates.weight)
async def validate_weight(msg: Message, state: FSMContext):
    try:
        w = float(msg.text.strip())
        await state.update_data(weight=w)
        await msg.answer("Please select your approximate level of physical activity:", reply_markup=kb.activity)
        await state.set_state(RegStates.activity)
    except ValueError:
        await msg.answer("Please enter a valid number for weight (e.g. 75).")


@start.callback_query(RegStates.activity, F.data == '1.2')
@start.callback_query(RegStates.activity, F.data == '1.375')
@start.callback_query(RegStates.activity, F.data == '1.55')
@start.callback_query(RegStates.activity, F.data == '1.725')
@start.callback_query(RegStates.activity, F.data == '1.9')
async def validate_activity(callback: CallbackQuery, state: FSMContext):
    activity = float(callback.data)
    await state.update_data(activity=activity)
    await bot.edit_message_text(text="Your goal:",
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=kb.goal)
    await state.set_state(RegStates.goal)


@start.callback_query(RegStates.goal, F.data == 'Weight loss')
@start.callback_query(RegStates.goal, F.data == 'Maintaining weight')
@start.callback_query(RegStates.goal, F.data == 'Mass gain')
async def validate_goal(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    goal = callback.data
    await state.update_data(goal=goal)
    data = await state.get_data()
    try:
        await add_user(session, callback.from_user.id, callback.from_user.username, data)
        await bot.edit_message_text(text="Registration is complete.\n"
                                         "Use /add to add food or /profile to view your profile.",
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    )
    except Exception as e:
        logger.error(f"Error processing registration: {e}")
        await callback.message.answer("Something went wrong...")

    await state.clear()


@start.message(Command('help'))
async def cmd_help(msg: Message):
    help_text = """
<b>What the bot can do:</b>
• Recognize 101 types of dishes
• Show prediction confidence

1. Send a photo of your food (not a file, just a photo)
2. I'll analyze the image
3. I'll confidently show you the top 3 most likely dishes

<em>For best results, submit clear photos of food against a plain background.</em>

<b>Main commands:</b>
/start - to start bot and get hi message.
/info - information about model.
/profile - to see your today meals
/add - to add your meal

If something is wrong please contact @olikooon.
    """

    await msg.answer(help_text, parse_mode=ParseMode.HTML)


@start.message(Command('info'))
async def cmd_info(msg: Message):
    info_text = """
<b>About the Model</b>

<b>Model:</b> Vision Transformer (ViT-B/16)
<b>Dataset:</b> Food-101
<b>Number of Classes:</b> 101
<b>Accuracy:</b> ~86% on the test set

The bot uses a modern Transformer architecture to classify food images. The model was trained on the Food-101 dataset, which contains 101 different categories of dishes.
    """

    await msg.answer(info_text, parse_mode=ParseMode.HTML)
