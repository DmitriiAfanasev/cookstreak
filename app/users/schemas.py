from datetime import datetime
from typing import Annotated, List, Optional
from zoneinfo import available_timezones

from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, HttpUrl, StringConstraints,
    field_validator,
)

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------- Полная модель документа (для внутреннего использования) ----------

class Users(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    hashed_password: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    dietary_preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_data: Optional[str] = None
    total_cooked_count: int = 0
    favorite_recipe_ids: List[PyObjectId] = Field(default_factory=list)
    is_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login_at: Optional[str] = None
    refresh_tokens: List[Optional[str]] = Field(default_factory=list)
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, extra="ignore", from_attributes=True)


class CollectionUsers(BaseModel):
    users: List[Users]


# ---------- Ответ: только безопасные поля (белый список) ----------

class UserProfile(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    dietary_preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    current_streak: int = 0
    longest_streak: int = 0
    total_cooked_count: int = 0
    favorite_recipe_ids: List[PyObjectId] = Field(default_factory=list)
    is_verified: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # extra="ignore" -> hashed_password, refresh_tokens и т.п. просто отбрасываются
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# ---------- Запрос на обновление ----------

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=30,
                                            pattern=r"^[a-zA-Z0-9_.]+$")]
DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Bio = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
Language = Annotated[str, StringConstraints(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")]  # en, ru, pt-BR
Tag = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
TagList = Annotated[List[Tag], Field(max_length=30)]

_TIMEZONES = available_timezones()


class UserProfileUpdate(BaseModel):
    display_name: Optional[DisplayName] = None
    username: Optional[Username] = None
    bio: Optional[Bio] = None
    avatar_url: Optional[HttpUrl] = None
    language: Optional[Language] = None
    timezone: Optional[str] = None
    dietary_preferences: Optional[TagList] = None
    allergies: Optional[TagList] = None
    goals: Optional[TagList] = None

    # Любое лишнее поле (current_streak, is_verified, hashed_password...) -> 422
    model_config = ConfigDict(extra="forbid")

    # Эти поля можно не передавать, но нельзя явно занулить
    # (валидатор срабатывает только на переданных значениях).
    @field_validator("display_name", "username", "dietary_preferences", "allergies", "goals",
                     mode="before")
    @classmethod
    def not_null(cls, v):
        if v is None:
            raise ValueError("Field cannot be null")
        return v

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, v):
        if v is not None and v not in _TIMEZONES:
            raise ValueError("Unknown timezone, expected IANA name like 'Europe/Belgrade'")
        return v

    @field_validator("dietary_preferences", "allergies", "goals")
    @classmethod
    def dedupe(cls, v):
        return list(dict.fromkeys(v)) if v is not None else v