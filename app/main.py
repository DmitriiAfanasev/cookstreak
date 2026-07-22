from fastapi import FastAPI
from .home.router import home_router

app = FastAPI()

app.include_router(home_router)