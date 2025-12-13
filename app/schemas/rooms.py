import datetime as dt
import enum
from typing import List, Self
from uuid import UUID

from pydantic import BaseModel, model_validator


class RoomType(enum.Enum):
	PUBLIC = "public"
	PRIVATE = "private"


class RoomUserCreate(BaseModel):
	user_id: int
	role: str = "reader"


class RoomUserInfo(RoomUserCreate):
	room_id: UUID

	class Config:
		from_attributes = True


class RoomCreate(BaseModel):
	name: str
	type: RoomType = RoomType.PUBLIC
	password: str | None = None

	@model_validator(mode='after')
	def type_validator(self) -> Self:
		if self.type == RoomType.PRIVATE and not self.password:
			raise ValueError("Password is required")
		return self


class RoomInfo(BaseModel):
	id: UUID
	name: str
	owner_id: int
	type: RoomType
	created_at: dt.datetime
	users: List[RoomUserInfo] = []

	class Config:
		from_attributes = True
