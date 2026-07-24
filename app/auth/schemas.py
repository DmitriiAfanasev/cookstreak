from pydantic import BaseModel, EmailStr

class AuthUser(BaseModel):
    email : EmailStr
    user_name : str 
    hashed_password : str