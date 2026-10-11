from datetime import timedelta

from authx import AuthX, AuthXConfig
from ..config import settings

auth_config = AuthXConfig(
    JWT_TOKEN_LOCATION=["headers"],
    JWT_PUBLIC_KEY=settings.JWT_PUBLIC_KEY,
    JWT_PRIVATE_KEY=settings.JWT_PRIVATE_KEY,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
    JWT_ALGORITHM="RS256",
)

auth_servies = AuthX(config=auth_config)