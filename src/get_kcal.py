import json
import logging
import time

import requests

from src.config import USDA_API_KEY, CLASSES_PATH
from src.database.engine import session_maker
from src.database.query import get_cal, add_cal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Reads 101 class
def load_food101_classes(path):
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]


# Getting all 101 classes of food in kcal per 100g
def get_kcal_for_food(name: str):
    params = {
        "api_key": USDA_API_KEY,
        "query": name,
        "pageSize": 1
    }

    for attempt in range(3):
        try:
            r = requests.get(SEARCH_URL, params=params, timeout=5)

            if r.status_code != 200:
                logger.error(f"USDA returned {r.status_code} for {name}")
                time.sleep(0.5)
                continue

            try:
                data = r.json()
            except json.JSONDecodeError:
                logger.error(f"USDA returned non-JSON for {name}")
                time.sleep(0.5)
                continue

            if "foods" not in data or not data["foods"]:
                return None

            food = data["foods"][0]
            for n in food.get("foodNutrients", []):
                if n.get("nutrientName", "").lower() == "energy" and n.get("unitName") == "KCAL":
                    return n.get("value")

            return None

        except Exception as e:
            logger.error(f"Error USDA {name}: {e}")
            time.sleep(0.5)

    return None


async def get_kcal():
    classes = load_food101_classes(CLASSES_PATH)

    async with session_maker() as session:

        for original in classes:
            name = " ".join(original.split("_")).capitalize()

            if await get_cal(session, name):
                continue

            logger.info(f"Searching for: {name}...")

            kcal = get_kcal_for_food(name)

            if kcal:
                logger.info(f"{name}: {kcal} kcal/100g")
                await add_cal(session, name, float(kcal))
            else:
                logger.error(f"not found {name}")
            time.sleep(0.5)
