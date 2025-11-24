import logging
from datetime import date

from PIL import Image
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot import keyboard as kb
from src.config import classifier
from src.database.query import get_user, get_meals, get_cal, add_meal, add_cal
from src.fsm.user import PhotoStates

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("cancel"), StateFilter("*"))
async def cancel_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await msg.answer("You are not in the process of filling out the form.")
        return

    await state.clear()
    await msg.answer("Action cancelled.")


@router.message(F.document)
async def handle_document(message: Message):
    if message.document.mime_type and message.document.mime_type.startswith('image/'):
        await message.answer(
            "<b>I see you sent an image file!</b>\n\n"
            "Please send the photo as a <b>photo</b> (not as a file) so I can process it.",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer("Please submit a <b>photo</b> of food for identification!",
                             parse_mode=ParseMode.HTML)


@router.message(Command('profile'))
async def cmd_profile(msg: Message, session: AsyncSession):
    user = await get_user(session, msg.from_user.id)
    if not user:
        await msg.answer("You are not registered. Press /start")
        return

    meals = await get_meals(session, msg.from_user.id)
    formula = {"Weight loss": 0.85, "Maintaining weight": 1, "Mass gain": 1.15}

    if user.gender in ['male', 'm']:
        cal = (((10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5) * user.activity) * formula[user.goal]
    else:
        cal = (((10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161) * user.activity) * formula[user.goal]

    text = f"Profile @{user.user_name}\nGoal: {user.goal}\nDaily calorie intake: {round(cal)}\n\n"

    if not meals:
        text += "There are no food entries yet. Press /add"
    else:
        cal_meal = 0.0
        text += "Today meals:\n"
        for m in meals:
            if m.created.date() == date.today():
                text += f"- {m.name}: {m.grams} г — {m.kcal:.1f} kcal\n"
                cal_meal += m.kcal
        text += f"\n\nThe remainder of the daily calorie intake {round(cal - cal_meal)}"

    await msg.answer(text, reply_markup=kb.history)


@router.callback_query(F.data == "history_by_days")
async def show_history(callback, session: AsyncSession):
    meals = await get_meals(session, callback.from_user.id)

    if not meals:
        await callback.message.edit_text("There are no food entries yet. Press /add.")
        return

    stats = {}
    for m in meals:
        day = m.created.date()
        stats.setdefault(day, 0)
        stats[day] += m.kcal

    text = "<b>History by days:</b>\n\n"
    for day, total in sorted(stats.items(), reverse=True):
        text += f"<b>{day}</b>: {total:.1f} kcal\n"

    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)


@router.message(Command('add'))
async def cmd_add(msg: Message, session: AsyncSession, state: FSMContext):
    user = await get_user(session, msg.from_user.id)
    if not user:
        await msg.answer("You are not registered. Press /start")
        return

    await msg.answer("Send a photo of the dish.")
    await state.set_state(PhotoStates.waiting_photo)


@router.message(PhotoStates.waiting_photo)
async def validate_photo(msg: Message, state: FSMContext):
    if not msg.photo:
        await msg.answer("Send a photo of the dish.")
        return

    photo = msg.photo[-1]
    file = await msg.bot.download(photo)
    img = Image.open(file)

    result = await classifier.predict_pil(img)

    if not result:
        await msg.answer("The dish was not recognized. Please enter the dish name manually:")
        await state.set_state(PhotoStates.confirm_name)
        return

    top = result[0]
    name = " ".join(top['class'].split('_')).capitalize()
    confidence = top['confidence']

    await state.update_data(pred_name=name)

    await msg.answer(
        f"I think it is <b>{name}</b> (confidence {confidence:.1f}%).\n"
        "Is this correct? (yes/no)",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(PhotoStates.confirm_prediction)


@router.message(PhotoStates.confirm_prediction)
async def confirm_prediction(msg: Message, state: FSMContext):
    answer = msg.text.lower().strip()

    if answer in ("yes", "y", "yeah", "ok"):
        await msg.answer("Great! Now enter the number of grams:")
        await state.set_state(PhotoStates.waiting_grams)
        return

    if answer in ("no", "n", "nope"):
        await msg.answer("Okay, please enter the name of the dish:")
        await state.set_state(PhotoStates.confirm_name)
        return

    # неправильный ввод
    await msg.answer('Please answer "yes" or "no".')


@router.message(PhotoStates.confirm_name)
async def validate_name(msg: Message, state: FSMContext):
    name = msg.text.strip().capitalize()
    await state.update_data(pred_name=name)
    await msg.answer("Please indicate the gram content of the dish (whole number of grams):")
    await state.set_state(PhotoStates.waiting_grams)
    return


@router.message(PhotoStates.waiting_grams)
async def validate_grams(msg: Message, session: AsyncSession, state: FSMContext):
    try:
        grams = float(msg.text.strip())
        data = await state.get_data()
        name = data.get('pred_name')

        cal = await get_cal(session, name)
        if not cal:
            await msg.answer(f"I didn't find <b>{name}</b> in the calorie database. "
                             f"Please enter the calorie content per 100g (kcal):",
                             parse_mode=ParseMode.HTML)
            await state.set_state(PhotoStates.ask_calories)
            await state.update_data(grams=grams)
            return
        kcal_per100 = cal.kcal_per_100
        total = kcal_per100 * grams / 100.0

        await add_meal(session, msg.from_user.id, name, grams, total)
        await msg.answer(f"Added: {name}, {grams} g — {total:.1f} kcal.")
        await state.clear()
    except ValueError:
        await msg.answer("Please enter the number of grams (e.g. 250).")


@router.message(PhotoStates.ask_calories)
async def validate_cal(msg: Message, session: AsyncSession, state: FSMContext):
    try:
        kcal100 = float(msg.text.strip())
        data = await state.get_data()
        name = data.get('pred_name')
        grams = data.get('grams')

        await add_cal(session, name, kcal100)
        total = kcal100 * grams / 100.0
        await add_meal(session, msg.from_user.id, name, grams, total)

        await msg.answer(f"Saved and added: <b>{name}</b>, {grams} g — {total:.1f} kcal.",
                         parse_mode=ParseMode.HTML)
        await state.clear()
    except ValueError:
        await msg.answer("Please enter the number (kcal per 100g).")


@router.message()
async def handle_other_messages(message: Message):
    await message.answer(
        "<b>Food Classifier Bot</b>\n\n"
        "Send me a <b>photo</b> of food, and I'll identify it!\n\n"
        "Use /help for help",
        parse_mode=ParseMode.HTML
    )
