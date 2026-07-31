import secrets

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from ..db.mongodb import users
from .schemas import AuthUser

auth_router = APIRouter()

@auth_router.get(
        "/get_user/{username}", 
        response_model_by_alias=False,
        tags=["Demo auth"])
def get_auth_user_username(username : str) -> str:
    corrent_user_db = users.find_one({"username" : username}, {"id" : 1, "email" : 1 , "username": 1, "hashed_password" : 1})
    corrent_user = AuthUser.model_validate(corrent_user_db)

    ###### U should create  check for password with corrent user

    """
    1. Попробовать взять модель pydantic но только сам хешированый пароль
        создание новой модели
    2. 
    """

    return corrent_user.hashed_password