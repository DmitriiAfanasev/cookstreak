import secrets
import hashlib

from datetime import datetime, timedelta, timezone

from typing import Dict
from bson import ObjectId

from passlib.hash import argon2

from pymongo.errors import DuplicateKeyError

from ..db.mongodb import users, tokens
from .schemas import RegisterRequest, TmpTokens
from ..core.schemas import UserRole

from ..core.config import auth_servies

def hash_token(token : str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def issue_refresh_token(user_id) -> TmpTokens:
    t = TmpTokens()
    token_refresh = secrets.token_urlsafe(32)
    token_access = auth_servies.create_access_token(uid=user_id)
    users.update_one({"_id" : ObjectId(user_id)}, {"$set" : {"refresh_tokens" : hash_token(token_refresh)}})
    t.acc = token_access
    t.ref = token_refresh
    return t

def rotate_refresh_token() -> TmpTokens:
    return None

# ---------- Регистрация ----------

DEFAULT_LANGUAGE = "ru"
DEFAULT_TIMEZONE = "UTC"
EMAIL_VERIFICATION_TTL = timedelta(hours=24)


class EmailAlreadyRegistered(Exception):
    pass


class UsernameAlreadyTaken(Exception):
    pass


def register_user(data: RegisterRequest) -> tuple[dict, str]:
    """Создаёт пользователя. Возвращает (документ из базы, токен подтверждения email в открытом виде)."""
    # 1. Уникальность
    if users.find_one({"email": data.email}, {"_id": 1}):
        raise EmailAlreadyRegistered()
    if data.username and users.find_one({"username": data.username}, {"_id": 1}):
        raise UsernameAlreadyTaken()

    now = datetime.now(timezone.utc)
    verification_token = secrets.token_urlsafe(32)

    # 2. Документ: из запроса берём только 4 разрешённых поля, остальное ставит сервер
    user = {
        "email": data.email,
        "hashed_password": argon2.hash(data.password),  # исходный пароль нигде не сохраняется
        "display_name": data.display_name,
        "avatar_url": None,
        "bio": None,
        "language": DEFAULT_LANGUAGE,
        "timezone": DEFAULT_TIMEZONE,
        "dietary_preferences": [],
        "allergies": [],
        "goals": [],
        "current_streak": 0,
        "longest_streak": 0,
        "total_cooked_count": 0,
        "last_activity_date": None,
        "favorite_recipe_ids": [],
        "is_verified": False,
        "is_active": True,
        "role": UserRole.USER.value,
        "email_verification_token": hash_token(verification_token),
        "email_verification_expires": now + EMAIL_VERIFICATION_TTL,
        "refresh_tokens": None,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    }
    # Без username поле не пишем вовсе (иначе индекс посчитает всех "без ника" дублями)
    if data.username:
        user["username"] = data.username

    # 3. Сохранение
    try:
        result = users.insert_one(user)
    except DuplicateKeyError as e:
        # Гонка: два одновременных запроса прошли проверки выше, индекс поймал второй
        key = (e.details or {}).get("keyPattern") or {}
        if "username" in key:
            raise UsernameAlreadyTaken()
        raise EmailAlreadyRegistered()

    user["_id"] = result.inserted_id
    return user, verification_token