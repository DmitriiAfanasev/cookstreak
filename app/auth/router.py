import secrets

from fastapi import APIRouter, HTTPException, status

from ..db.mongodb import users
from .schemas import AuthUser
from ..users.schemas import Users

auth_router = APIRouter()

@auth_router.get(
        "/get_user/{username}", 
        # response_model=Users,
        response_model_by_alias=False,
        tags=["Demo auth"])
def get_auth_user_username(username : str) -> str:
    corrent_user_db = users.find_one({"username" : username})
    corrent_user = Users.model_validate(corrent_user_db)

    ###### U should create  check for password with corrent user

    return corrent_user.hashed_password