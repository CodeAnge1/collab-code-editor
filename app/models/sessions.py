import datetime as dt
import uuid

from sqlalchemy import text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Session(Base):
	__tablename__ = "sessions"

	session_id: Mapped[uuid.UUID] = mapped_column(
		Uuid(as_uuid=True),
		primary_key=True,
		server_default=text("gen_random_uuid()")
	)
	user_id: Mapped[int] = mapped_column(
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False
	)
	created_at: Mapped[dt.datetime] = mapped_column(
		server_default=text("TIMEZONE('utc', now())")
	)
	expires_at: Mapped[dt.datetime] = mapped_column(
		nullable=False
	)

	user: Mapped["User"] = relationship(
		"User",
		back_populates="sessions"
	)
