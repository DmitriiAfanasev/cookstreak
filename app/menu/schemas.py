from datetime import date
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class MenuIngredient(BaseModel):
    amount: Optional[Union[str, int, float]] = None
    unit: Optional[str] = None
    item: str = ""

    model_config = ConfigDict(extra="ignore")


class MenuRecipe(BaseModel):
    """Снимок рецепта внутри меню (не зависит от того, как потом поменяется рецепт в базе)."""
    recipe_id: PyObjectId
    title: str
    meal_type: Optional[str] = None
    servings: Optional[Union[str, int]] = None
    intro: Optional[str] = None
    ingredients: List[MenuIngredient] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    source: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class MenuDay(BaseModel):
    day_of_week: str          # monday ... sunday
    date: date
    recipes: List[MenuRecipe]


class WeeklyMenu(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    year: int                 # ISO-год (может отличаться от календарного в конце декабря / начале января)
    week: int                 # ISO-номер недели 1..53
    week_start: date
    week_end: date
    days: List[MenuDay]
    warnings: List[str] = Field(default_factory=list)
    generated_at: str

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
