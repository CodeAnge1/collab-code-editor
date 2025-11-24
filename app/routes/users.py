from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud import get_user_by_credentials, get_user_by_username, get_user_by_email, create_user
from app.config import settings
from app.db import get_session
from app.models import User
from app.schemas.users import *
from app.utils import create_access_token, create_refresh_token, get_current_user, verify_password, refresh_access_token

router = APIRouter(
	prefix="/users",
	tags=["users"]
)


@router.post("/register", response_model=UserInfo)
def register(user: UserAdd, db: Session = Depends(get_session)):
	if get_user_by_username(db, user.username):
		raise HTTPException(status_code=400, detail="Username already registered")
	if get_user_by_email(db, str(user.email)):
		raise HTTPException(status_code=400, detail="Email already registered")
	created_user = create_user(db, user)
	user_info = UserInfo(
		id=created_user.id,
		username=created_user.username,
		email=created_user.email
	)
	return user_info


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session), response: Response = None):
	user = get_user_by_credentials(db, form_data.username, form_data.username)
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password"
		)
	data = {
		"sub": str(user.username),
	}
	access_tok = create_access_token(data)
	refresh_tok = create_refresh_token(data)
	response.set_cookie(
		key="access_token",
		value=access_tok,
		max_age=settings.jwt_cfg.access_token_expire_minutes * 60,
		path="/",
		samesite="strict",
		secure=True,
		httponly=True,
	)
	response.set_cookie(
		key="refresh_token",
		value=refresh_tok,
		max_age=settings.jwt_cfg.refresh_token_expire_days * 24 * 3600,
		path="/",
		samesite="strict",
		secure=True,
		httponly=True,
	)
	return {"msg": "Login successful"}


@router.post("/refresh")
def refresh_token(new_access_token: str = Depends(refresh_access_token), response: Response = None):
	if not new_access_token:
		raise HTTPException(401, "No refresh token provided")
	response.set_cookie(
		key="access_token",
		value=new_access_token,
		max_age=settings.jwt_cfg.access_token_expire_minutes * 60,
		path="/",
		samesite="strict",
		secure=True,
		httponly=True,
	)
	return {"msg": "Access token refreshed"}


@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
	result = UserInfo(
		id=current_user.id,
		username=current_user.username,
		email=current_user.email
	)
	return result
