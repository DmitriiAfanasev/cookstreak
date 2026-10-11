from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"


def load_key(value: Optional[str], filename: str) -> str:
    if value:
        return value.replace("\\n", "\n")
    path = CERTS_DIR / filename
    if not path.is_file():
        raise ValueError(f"JWT key not found: set the env variable or create {path}")
    return path.read_text()


class Settings(BaseSettings):
    MONGO_URL : str
    MONGO_PORT : int
    JWT_PRIVATE_KEY : Optional[str] = None
    JWT_PUBLIC_KEY : Optional[str] = None

    @model_validator(mode="after")
    def load_jwt_keys(self):
        self.JWT_PRIVATE_KEY = load_key(self.JWT_PRIVATE_KEY, "jwt-private.pem")
        self.JWT_PUBLIC_KEY = load_key(self.JWT_PUBLIC_KEY, "jwt-public.pem")
        return self

    class Config:
        env_file = ".env"


settings = Settings()
