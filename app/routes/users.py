from fastapi import APIRouter

from ..schemas import *

router = APIRouter(
	prefix="/users",
	tags=["users"]
)


@router.post("/register")
def register(user: UserAdd):
	pass


@router.post("/login")
def login(user: UserLogin):
	pass
