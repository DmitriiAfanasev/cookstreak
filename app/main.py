import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .home.router import home_router
from .users.router import users_router

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(home_router)
app.include_router(users_router)

 
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
