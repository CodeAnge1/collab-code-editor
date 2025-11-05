from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.db import create_tables
from .routes import users


@asynccontextmanager
async def lifespan(app: FastAPI):
	create_tables()
	yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)


@app.get("/")
async def read_root():
	return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
	return {"item_id": item_id, "q": q}
