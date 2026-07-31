from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]

class AuthUser(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    email : EmailStr
    username : Optional[str] = Field(alias="username", default=None)
    hashed_password : str


class AuthSign(BaseModel):
    email : EmailStr
    password : str

class Tokens(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id : Optional[str] = Field(alias="user_id", default=None)
    token_hash : Optional[str] = Field(alias="token_hash", default=None)
    device_info : Optional[str] = None
    created_at : Optional[datetime]
    expires_at : Optional[datetime]
    revoked : Optional[bool] = None

class TmpTokens(BaseModel):
    ref : Optional[str] = None
    acc : Optional[str] = None