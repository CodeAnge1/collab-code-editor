import datetime as dt
from typing import List

from pydantic import BaseModel


class RoomUserCreate(BaseModel):
	user_id: int
	role: str = "reader"


class RoomUserInfo(RoomUserCreate):
	room_id: int

	class Config:
		from_attributes = True


class RoomCreate(BaseModel):
	name: str


class RoomInfo(RoomCreate):
	id: int
	owner_id: int
	created_at: dt.datetime
	users: List[RoomUserInfo] = []

	class Config:
		from_attributes = True
