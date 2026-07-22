from pymongo import MongoClient
from ..config import Settings

settings = Settings()

client = MongoClient(settings.MONGO_URL, port=settings.PORT)

foods_db = client["food-db"]
foods = foods_db['foods']

users_db = client["user-db"]
users = users_db['users']