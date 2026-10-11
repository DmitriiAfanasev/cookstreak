from pymongo import MongoClient
from pymongo.errors import OperationFailure

from ..config import settings

client = MongoClient(settings.MONGO_URL, port=settings.PORT)

foods_db = client["food-db"]
foods = foods_db["foods"]

users_db = client["user-db"]
users = users_db["users"]

try:
    users.create_index("username", unique=True)
except OperationFailure as e:
    print(f"WARNING: username index not created: {e}")