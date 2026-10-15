from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from ..auth.dependencies import get_current_user
from ..db.mongodb import users
from .schemas import UserProfile, UserProfileUpdate

users_router = APIRouter()

USERNAME_TAKEN = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")


@users_router.get("/all_users", response_model=list[UserProfile], tags=["User"])
def get_all_users(current_user: dict = Depends(get_current_user)):
    # Только безопасные поля: без hashed_password и refresh_tokens
    return [UserProfile.model_validate(u) for u in users.find({})]


@users_router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserProfile.model_validate(current_user)


@users_router.patch("/me", response_model=UserProfile)
def update_me(data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    # exclude_unset -> только реально переданные поля; mode="json" -> HttpUrl станет строкой
    updates = data.model_dump(exclude_unset=True, mode="json")

    if not updates:
        return UserProfile.model_validate(current_user)

    new_username = updates.get("username")
    if new_username and new_username != current_user.get("username"):
        taken = users.find_one(
            {"username": new_username, "_id": {"$ne": current_user["_id"]}},
            {"_id": 1},
        )
        if taken:
            raise USERNAME_TAKEN

    updates["updated_at"] = datetime.now(timezone.utc)

    try:
        updated = users.find_one_and_update(
            {"_id": current_user["_id"]},  # только свой профиль: id берётся из токена
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError:
        raise USERNAME_TAKEN

    if updated is None:  # удалили между проверкой токена и апдейтом
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfile.model_validate(updated)