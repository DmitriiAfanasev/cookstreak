from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.dependencies import get_current_user
from .schemas import WeeklyMenu
from .service import NotEnoughRecipesError, get_or_create_current_menu

menu_router = APIRouter(prefix="/menu", tags=["menu"])


@menu_router.get(
    "/current-week",
    response_model=WeeklyMenu,
    responses={404: {"description": "Not enough suitable recipes for this user's profile"}},
)
def get_current_week_menu(current_user: dict = Depends(get_current_user)):
    # Неделя всегда вычисляется на сервере: параметров year/week у эндпоинта нет,
    # поэтому запросить прошлую или будущую неделю через него нельзя.
    try:
        menu = get_or_create_current_menu(current_user)
    except NotEnoughRecipesError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Not enough suitable recipes to build a menu for this week",
                "found": e.found,
                "required": e.required,
                "hint": "Relax dietary preferences or allergies, or add more recipes",
            },
        )
    return WeeklyMenu.model_validate(menu)
