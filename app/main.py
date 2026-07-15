from fastapi import FastAPI
from pymongo import MongoClient
from .recipes.schemas import CollectionRecipes
from .config import Settings
app = FastAPI()
settings = Settings()

client = MongoClient(settings.MONGO_URL, port=settings.PORT)

foods_db = client["food-db"]

foods = foods_db['foods']

@app.get('/')
async def root():
    return {"msg" : "cookstreak"}

@app.get('/db')
def db():
    data = foods.find()
    return CollectionRecipes(recipes = foods.find().to_list(100)) 