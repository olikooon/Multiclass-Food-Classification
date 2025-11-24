from dotenv import find_dotenv, load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Meal, Calories

load_dotenv(find_dotenv())


async def get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.tg_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def add_user(session: AsyncSession, user_id: int, username: str, data: dict) -> None:
    session.add(User(
        tg_id=user_id,
        user_name=username,
        gender=data.get('gender'),
        age=data.get('age'),
        height=data.get('height'),
        weight=data.get('weight'),
        activity=data.get('activity'),
        goal=data.get('goal')
    ))
    await session.commit()


async def add_meal(session: AsyncSession, user_id: int, name: str, grams: float, total: float) -> None:
    session.add(Meal(
        user_id=user_id,
        name=name,
        grams=grams,
        kcal=total
    ))
    await session.commit()


async def add_cal(session: AsyncSession, name: str, kcal100: float) -> None:
    session.add(Calories(
        name=name,
        kcal_per_100=kcal100
    ))
    await session.commit()


async def get_meals(session: AsyncSession, user_id: int):
    query = select(Meal).where(Meal.user_id == user_id).order_by(Meal.created.desc())
    result = await session.execute(query)
    return result.scalars().all()


async def get_cal(session: AsyncSession, name: str):
    query = select(Calories).where(Calories.name == name)
    result = await session.execute(query)
    return result.scalars().first()

