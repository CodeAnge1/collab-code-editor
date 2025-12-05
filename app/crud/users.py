from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users import UserAdd
from app.utils.security import get_password_hash


def get_user_by_id(db: Session, user_id: int) -> User | None:
	user = db.query(User).filter(User.id == user_id).first()
	return user


def get_user_by_username(db: Session, username: str) -> User | None:
	user = db.query(User).filter(User.username == username).first()
	return user


def get_user_by_email(db: Session, email: str) -> User | None:
	user = db.query(User).filter(User.email == email).first()
	return user


def get_user_by_credentials(db: Session, name_or_email: str) -> User | None:
	if "@" in name_or_email:
		user = get_user_by_email(db, name_or_email)
	else:
		user = get_user_by_username(db, name_or_email)
	return user


def create_user(db: Session, user: UserAdd) -> User:
	hashed_password = get_password_hash(user.password)
	new_user = User(
		username=user.username,
		email=str(user.email),
		hashed_password=hashed_password
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user
