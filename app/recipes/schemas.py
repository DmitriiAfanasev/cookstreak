from typing import Annotated, Optional, List, Union

from pydantic import BaseModel, BeforeValidator, Field, ConfigDict


PyObjectId = Annotated[str, BeforeValidator(str)]

class Ingredient(BaseModel):
    amount : Optional[Union[str, int]] = None
    unit :Optional[str]
    item : str


class Recipe(BaseModel):
    id : Optional[PyObjectId] = Field(alias="_id", default=None)
    week : Optional[str]
    meal_type : Optional[str]
    menu : str
    day_of_week : Optional[str] = None
    title : str
    servings : Optional[Union[str, int]] = None
    intro : str
    tips : List[str]
    ingredients : List[Ingredient]
    instructions : List[str]
    source : str
    model_config = ConfigDict(populate_by_name=True)

class CollectionRecipes(BaseModel):
    recipes : List[Recipe]

