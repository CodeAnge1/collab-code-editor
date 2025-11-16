from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import users


@asynccontextmanager
async def lifespan(_app: FastAPI):
	yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)


@app.get("/")
async def read_root():
	return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
	return {"item_id": item_id, "q": q}
