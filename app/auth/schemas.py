from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, BeforeValidator, Field, field_validator

from ..users.schemas import DisplayName, Username

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


# ---------- Регистрация ----------

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128  # верхняя граница: длинные строки зря грузят argon2


class RegisterRequest(BaseModel):
    """Всё, что клиент может прислать при регистрации. Любое другое поле -> 422."""
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    display_name: DisplayName
    username: Optional[Username] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        # Anna@Example.com и anna@example.com — один и тот же адрес
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.strip() != v:
            raise ValueError("Password must not start or end with whitespace")
        missing = []
        if not any(c.islower() for c in v):
            missing.append("a lowercase letter")
        if not any(c.isupper() for c in v):
            missing.append("an uppercase letter")
        if not any(c.isdigit() for c in v):
            missing.append("a digit")
        if missing:
            raise ValueError("Password must contain " + ", ".join(missing))
        return v


class RegisterResponse(BaseModel):
    id: PyObjectId
    email: EmailStr
    username: Optional[str] = None
    display_name: str
    is_verified: bool
    created_at: datetime
    message: str