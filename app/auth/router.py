import secrets

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from passlib.hash import argon2

from ..db.mongodb import users
from .schemas import AuthUser
from .services import auth_servies

auth_router = APIRouter()

@auth_router.get("/login", response_model_by_alias=False, tags=["Demo auth"])
def get_auth_user_username(username : str, password : str) -> str:
    corrent_user_db = users.find_one({"username" : username}, {"id" : 1, "email" : 1 , "username": 1, "hashed_password" : 1})
    corrent_user = AuthUser.model_validate(corrent_user_db)

    if argon2.verify(password, corrent_user.hashed_password):
        token_refresh = auth_servies.create_refresh_token(uid=corrent_user.id)
        token_access = auth_servies.create_access_token(uid=corrent_user.id)
        users.update_one({"username" : corrent_user.username}, {"$set" : {"refresh_tokens" : token_refresh}})
        return token_access
    raise status.HTTP_401_UNAUTHORIZED