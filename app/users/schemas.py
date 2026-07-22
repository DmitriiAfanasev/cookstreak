from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import Field, BeforeValidator, BaseModel, EmailStr, ConfigDict

PyObjectId = Annotated[str, BeforeValidator(str)]

class Users(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    email : EmailStr
    hashed_password : str
    username : str
    display_name : str
    avatar_url : Optional[str]
    bio : Optional[str]
    language : Optional[str]
    timezone : Optional[str]
    dietary_preferences : Optional[List[str]]
    allergies : Optional[List[str]]
    goals : Optional[List[str]]
    current_streak : int = 0
    longest_streak : int = 0
    last_activity_data : Optional[str] = None 
    total_cooked_count : int
    favorite_recipe_ids : List[PyObjectId]
    is_verified : bool
    email_verification_token : Optional[str] = None
    email_verification_expires : Optional[datetime] = None
    is_active : bool
    created_at : Optional[str]
    updated_at : Optional[str]
    last_login_at : Optional[str]
    refresh_tokens : Optional[List[Optional[str]]] = Field(default_factory=list)
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

class CollectionUsers(BaseModel):
    users : List[Users]