from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_session
from ..models import User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_password_hash(password: str) -> str:
	return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: int = settings.jwt_cfg.access_token_expire_minutes):
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(
		payload=to_encode,
		key=settings.jwt_cfg.secret_key.get_secret_value(),
		algorithm=settings.jwt_cfg.algorithm
	)
	return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
	from ..crud import get_user_by_username

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		decoded_token = jwt.decode(
			jwt=token,
			key=settings.jwt_cfg.secret_key.get_secret_value(),
			algorithms=[settings.jwt_cfg.algorithm]
		)
		username: str | None = decoded_token["sub"]
		if not username:
			raise credentials_exception
	except jwt.PyJWTError:
		raise credentials_exception

	current_user = get_user_by_username(db, username)
	if not current_user:
		raise credentials_exception
	return current_user
