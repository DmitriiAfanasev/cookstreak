from pymongo import MongoClient
from pymongo.errors import OperationFailure

from ..config import settings

client = MongoClient(settings.MONGO_URL, port=settings.MONGO_PORT)

foods_db = client["food-db"]
foods = foods_db["foods"]

users_db = client["user-db"]
users = users_db["users"]
menus = users_db["menus"]

for name, keys, options in (
    ("email_unique", "email", {}),
    # partial: юзеры без username не конфликтуют между собой
    ("username_unique", "username", {"partialFilterExpression": {"username": {"$type": "string"}}}),
):
    try:
        users.create_index(keys, name=name, unique=True, **options)
    except OperationFailure as e:
        print(f"WARNING: index {name} not created: {e}")

refresh_tokens_db = client["refresh_tokens"]
tokens = refresh_tokens_db["tokens"]
