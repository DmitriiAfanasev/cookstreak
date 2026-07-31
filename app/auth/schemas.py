from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]

class AuthUser(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    email : EmailStr
    username : str 
    hashed_password : str