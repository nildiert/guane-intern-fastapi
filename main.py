import requests
import uuid
from datetime import datetime as dt
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from models import DogsList, DogDelete
from db import database, dogs


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/api/dogs', response_model=List[DogsList])
async def get_dogs():
    query = dogs.select()
    return await database.fetch_all(query)


@app.get('/api/dogs/is_adopted', response_model=List[DogsList])
async def get_adopted():
    query = dogs.select().where(dogs.c.is_adopted)
    return await database.fetch_all(query)


@app.get('/api/dogs/{name}', response_model=DogsList)
async def get_dog(name: str):
    query = dogs.select().where(dogs.c.name == name)
    return await database.fetch_one(query)


@app.post('/api/dogs/{name}', response_model=DogsList)
async def create_dog(name: str, adopted: bool):
    gID = str(uuid.uuid1())
    gDate = str(dt.now())

    # getting random image in dog ceo API
    response = requests.get('https://dog.ceo/api/breeds/image/random').json()
    dog_image_url = response['message']

    query = dogs.insert().values(
        id=gID,
        name=name,
        picture=dog_image_url,
        create_date=gDate,
        is_adopted=adopted
    )
    await database.execute(query)
    return {
        "id": gID,
        "name": name,
        "picture": dog_image_url,
        "create_date": gDate,
        "is_adopted": adopted
    }


@app.put('/api/dogs/{name}', response_model=DogsList)
async def update_dog(name: str, adopted: bool):
    gDate = str(dt.now())
    query = dogs.update().where(dogs.c.name == name).values(
        name=name,
        is_adopted=adopted,
        create_date=gDate
    )
    await database.execute(query)

    return await get_dog(name)


@app.delete('/api/dogs/{name}')
async def delete_dog(dog: DogDelete):
    query = dogs.delete().where(dogs.c.name == dog.name)
    print(query)
    await database.execute(query)

    return {
        "status": True,
        "message": "This dog has been deleted successfully"
    }
