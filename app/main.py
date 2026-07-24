from fastapi import FastAPI
from .home.router import home_router
from .users.router import users_router
from .auth.router import auth_router

app = FastAPI()

app.include_router(home_router)
app.include_router(users_router)
app.include_router(auth_router)