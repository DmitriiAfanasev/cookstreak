from bson import ObjectId
from bson.errors import InvalidId
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings
from ..core.config import auth_config
from ..db.mongodb import users

# auto_error=False: сами отдаём 401 (иначе в части версий FastAPI будет 403)
bearer_scheme = HTTPBearer(auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing access token",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if creds is None:
        raise credentials_exception

    try:
        payload = jwt.decode(
            creds.credentials,
            settings.JWT_PUBLIC_KEY,
            algorithms=[auth_config.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:  # просрочен, битая подпись, мусор
        raise credentials_exception

    if payload.get("type") != "access":  # refresh-токеном сюда не пустим
        raise credentials_exception

    try:
        user_id = ObjectId(payload.get("sub"))
    except (InvalidId, TypeError):
        raise credentials_exception

    user = users.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user