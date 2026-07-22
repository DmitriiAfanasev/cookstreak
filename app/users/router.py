from fastapi import APIRouter
from .schemas import CollectionUsers
from ..db.mongodb import users

users_router = APIRouter()

@users_router.get('/all_users')
def get_all_users():
    return CollectionUsers(users=users.find({}))