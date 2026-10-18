import logging

import secrets
import hashlib

from typing import Dict
from bson import ObjectId

from fastapi import Depends, APIRouter, HTTPException, status
from passlib.hash import argon2

from ..db.mongodb import users
from .schemas import AuthUser, AuthSign, RegisterRequest, RegisterResponse
from ..core.config import auth_servies
from .services import (
    EmailAlreadyRegistered, UsernameAlreadyTaken, issue_refresh_token, register_user,
)

logger = logging.getLogger(__name__)

auth_router = APIRouter()

@auth_router.post("/auth/login", response_model_by_alias=False, tags=["Auth"])
def login(authSign : AuthSign) -> Dict:
    current_user_db = users.find_one({"email" : authSign.email.strip().lower()}, {"_id" : 1, "email": 1, "hashed_password" : 1})

    if not current_user_db:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    current_user = AuthUser.model_validate(current_user_db)

    try:
        password_ok = argon2.verify(authSign.password, current_user.hashed_password)
    except ValueError:  # в базе не argon2-хеш (старые/тестовые юзеры) -> 401, а не 500
        password_ok = False

    if password_ok:
        token = issue_refresh_token(current_user.id)
        return {"access" : token.acc, "refresh" : token.ref, "token_type" : "bearer"}
    raise HTTPException(status_code=401, detail="Неверный email или пароль")

@auth_router.post("/auth/refresh", response_model_by_alias=False, tags=["Demo Auth"])
def refresh_token():
    pass

@auth_router.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    responses={400: {"description": "Email or username already registered"}},
    tags=["Auth"],
)
def register(data: RegisterRequest):
    try:
        user, verification_token = register_user(data)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    except UsernameAlreadyTaken:
        raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")

    # TODO: отправить письмо со ссылкой. Пока писем нет, токен пишется в лог для локальной проверки
    logger.warning("Email verification token for %s: %s", user["email"], verification_token)

    return RegisterResponse(
        id=user["_id"],
        email=user["email"],
        username=user.get("username"),
        display_name=user["display_name"],
        is_verified=user["is_verified"],
        created_at=user["created_at"],
        message="Регистрация прошла успешно. Подтвердите email по ссылке из письма.",
    )