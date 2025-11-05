from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..crud import get_user_by_username, get_user_by_email, create_user
from ..db import get_session
from ..models import User
from ..schemas.users import *
from ..utils import create_access_token, get_current_user, verify_password

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
	user = get_user_by_username(db, form_data.username)
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}
		)
	data = {
		"sub": str(user.username),
	}
	result = {
		"access_token": create_access_token(data),
		"token_type": "bearer"
	}
	return result


@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
	result = UserInfo(
		id=current_user.id,
		username=current_user.username,
		email=current_user.email
	)
	return result
