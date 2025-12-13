from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import get_user_by_credentials, get_user_by_username, get_user_by_email, create_user
from app.crud.sessions import create_session, revoke_session
from app.db import get_session
from app.models import User
from app.schemas.users import *
from app.utils import verify_password, get_current_user

router = APIRouter(
	prefix="/users",
	tags=["users"]
)


def set_session_cookie(user_id: int, db: Session, response: Response):
	session_id = create_session(db, user_id=user_id)
	response.set_cookie(
		key="session_id",
		value=str(session_id),
		httponly=True,
		secure=True,
		samesite="lax",
		expires=settings.sess_cfg.expire_days * 24 * 60 * 60
	)


@router.post("/register")
def register(user: UserAdd, db: Session = Depends(get_session), response: Response = None):
	if get_user_by_username(db, user.username):
		raise HTTPException(status_code=400, detail="Username already registered")
	if get_user_by_email(db, str(user.email)):
		raise HTTPException(status_code=400, detail="Email already registered")
	created_user = create_user(db, user)
	set_session_cookie(created_user.id, db, response)
	return {"msg": "Login successful"}


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_session), response: Response = None):
	user = get_user_by_credentials(db, user_data.username_or_email)
	if not user or not verify_password(user_data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password"
		)
	set_session_cookie(user.id, db, response)
	return {"msg": "Login successful"}


@router.post("/logout")
def logout(session_id: str | None = Cookie(None), db: Session = Depends(get_session), response: Response = None):
	if session_id:
		revoke_session(db, session_id)
	response.delete_cookie(key="session_id")
	return {"msg": "Logout successful"}


@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
	result = UserInfo(
		id=current_user.id,
		username=current_user.username,
		email=current_user.email
	)
	return result
