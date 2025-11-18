import datetime as dt
from typing import Annotated, List

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

created_at = Annotated[dt.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Room(Base):
	__tablename__ = "rooms"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(100))
	owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	created_at: Mapped[created_at]

	users: Mapped[List[RoomUser]] = relationship(
		"RoomUser",
		back_populates="room",
		cascade="all, delete-orphan",
		passive_deletes=True
	)


class RoomUser(Base):
	__tablename__ = "room_users"

	room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	role: Mapped[str] = mapped_column(String(20), default="reader")

	room: Mapped[Room] = relationship("Room", back_populates="users")
	user: Mapped["User"] = relationship("User", back_populates="room_users")
