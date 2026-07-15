from typing import Annotated, Optional
from pydantic import Field, BeforeValidator, BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    name : str
    email : EmailStr
    phone_number : PhoneNumber
