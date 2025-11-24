import os

from aiogram import Bot
from dotenv import load_dotenv

from src.model.model import FoodClassificationService

load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")

MODEL_PATH = "src/model/vit_food_101.pth"
CLASSES_PATH = "src/model/classes.txt"
classifier = FoodClassificationService(MODEL_PATH, CLASSES_PATH)
bot = Bot(token=os.getenv("BOT_TOKEN"))
