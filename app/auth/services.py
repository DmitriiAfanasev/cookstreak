from datetime import timedelta

from authx import AuthX, AuthXConfig
from ..config import private_key, public_key

auth_config = AuthXConfig(
    JWT_TOKEN_LOCATION=["headers"],
    JWT_PUBLIC_KEY = public_key,
    JWT_PRIVATE_KEY=private_key,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
    JWT_ALGORITHM="RS256"
)

auth_servies = AuthX(config=auth_config)