from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String(40), unique=True)
	email: Mapped[str] = mapped_column(String(256), unique=True)
	hashed_password: Mapped[str] = mapped_column(nullable=False)

	room_users: Mapped[List["RoomUser"]] = relationship(
		"RoomUser",
		back_populates="user"
	)
	sessions: Mapped[List["Session"]] = relationship(
		"Session",
		back_populates="user",
		cascade="all, delete-orphan",
		passive_deletes=True
	)
