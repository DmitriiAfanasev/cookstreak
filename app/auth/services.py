import secrets
import hashlib

from typing import Dict
from bson import ObjectId

from passlib.hash import argon2

from ..db.mongodb import users, tokens
from .schemas import TmpTokens

from ..core.config import auth_servies

def hash_token(token : str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def issue_refresh_token(user_id) -> TmpTokens:
    t = TmpTokens()
    token_refresh = secrets.token_urlsafe(32)
    token_access = hash_token(auth_servies.create_access_token(uid=user_id))
    users.update_one({"_id" : ObjectId(user_id)}, {"$set" : {"refresh_tokens" : token_refresh}})
    t.acc = token_access
    t.ref = token_refresh
    return t

def rotate_refresh_token() -> TmpTokens:
    return None