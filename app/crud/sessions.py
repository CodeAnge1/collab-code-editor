from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.models.sessions import Session as SessionModel


def create_session(db: Session, user_id: int, expire_days=settings.sess_cfg.expire_days) -> UUID:
	session = SessionModel(
		user_id=user_id,
		expires_at=datetime.now(timezone.utc) + timedelta(days=expire_days),
	)
	db.add(session)
	db.commit()

	return session.session_id


def revoke_session(db: Session, session_id: str) -> None:
	session = db.query(SessionModel).filter(SessionModel.session_id == UUID(session_id)).first()
	if session:
		db.delete(session)
		db.commit()


def update_session_expire_time(db: Session, session: SessionModel | None,
							   expire_days: int = settings.sess_cfg.expire_days) -> None:
	if session:
		session.expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
		db.commit()


def get_user_by_session_id(db: Session, session_id: str) -> User | None:
	session = db.query(SessionModel).filter(SessionModel.session_id == UUID(session_id)).first()
	update_session_expire_time(db, session)
	return session.user if session else None
