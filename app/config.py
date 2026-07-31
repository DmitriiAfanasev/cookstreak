from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent

PRIVATE_KEY_PATH = BASE_DIR / "certs" / "jwt-private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "certs" / "jwt-public.pem"

private_key = PRIVATE_KEY_PATH.read_text()
public_key = PUBLIC_KEY_PATH.read_text()

class Settings(BaseSettings):
    MONGO_URL : str
    PORT : int

    
    class Config:
        env_file = ".env"

