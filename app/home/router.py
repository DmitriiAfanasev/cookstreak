from datetime import datetime

from fastapi import APIRouter
from ..recipes.schemas import CollectionRecipes
from ..db.mongodb import foods

home_router = APIRouter()

@home_router.get('/home')
def current_week():
    week = datetime.now().isocalendar()[1]
    data = foods.find({"week" : str(week)})
    return CollectionRecipes(recipes=data)

@home_router.get('/all')
def get_all():
    return CollectionRecipes(recipes=foods.find({}))