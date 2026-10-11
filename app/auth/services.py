from datetime import datetime, timedelta, timezone

import jwt

from ..config import settings


def create_access_token(user_id: str) -> str:
    """Контракт токена, на который опирается get_current_user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)