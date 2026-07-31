import secrets
import hashlib

from typing import Dict
from bson import ObjectId

from fastapi import Depends, APIRouter, HTTPException
from passlib.hash import argon2

from ..db.mongodb import users
from .schemas import AuthUser, AuthSign
from ..core.config import auth_servies
from .services import issue_refresh_token

auth_router = APIRouter()

@auth_router.post("/auth/login", response_model_by_alias=False, tags=["Auth"])
def login(authSign : AuthSign) -> Dict:
    current_user_db = users.find_one({"email" : authSign.email}, {"_id" : 1, "email": 1, "hashed_password" : 1})

    if not current_user_db:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    current_user = AuthUser.model_validate(current_user_db)

    if argon2.verify(authSign.password, current_user.hashed_password):
        token = issue_refresh_token(current_user.id)
        return {"access" : token.acc, "refresh" : token.ref, "token_type" : "bearer"}
    raise HTTPException(status_code=401, detail="Неверный email или пароль")

@auth_router.post("/auth/refresh", response_model_by_alias=False, tags=["Demo Auth"])
def refresh_token():
    pass