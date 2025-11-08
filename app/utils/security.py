from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status, Cookie
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_session
from ..models import User

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
	return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return password_hash.verify(plain_password, hashed_password)


def create_token(data: dict, token_type: str, expire: datetime):
	data_copy = data.copy()
	data_copy.update({"exp": expire})
	data_copy.update({"token_type": token_type})
	encoded_jwt = jwt.encode(
		payload=data_copy,
		key=settings.jwt_cfg.secret_key.get_secret_value(),
		algorithm=settings.jwt_cfg.algorithm
	)
	return encoded_jwt


def create_access_token(data: dict, expires_delta: int = settings.jwt_cfg.access_token_expire_minutes):
	expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
	return create_token(data, "access", expire)


def create_refresh_token(data: dict, expires_delta: int = settings.jwt_cfg.refresh_token_expire_days):
	expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
	return create_token(data, "refresh", expire)


def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_session)) -> User:
	from ..crud import get_user_by_username

	if not access_token:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="No access token provided",
		)

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
	)
	try:
		decoded_token = jwt.decode(
			jwt=access_token,
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


def refresh_access_token(refresh_token: str = Cookie(None), db: Session = Depends(get_session)):
	from ..crud import get_user_by_username

	if not refresh_token:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="No access token provided",
		)

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Invalid refresh token",
	)
	try:
		decoded_token = jwt.decode(
			jwt=refresh_token,
			key=settings.jwt_cfg.secret_key.get_secret_value(),
			algorithms=[settings.jwt_cfg.algorithm]
		)
		username = decoded_token["sub"]
		token_type = decoded_token["token_type"]
		if not username or token_type != "refresh":
			raise credentials_exception
	except jwt.PyJWTError:
		raise credentials_exception
	user = get_user_by_username(db, username)
	if not user:
		raise credentials_exception
	data = {
		"sub": str(user.username),
	}
	return create_access_token(data)
