from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import User
from app.crud.sessions import get_user_by_session_id


def get_current_user(session_id: str | None = Cookie(None), db: Session = Depends(get_session)) -> User:
	if not session_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	user = get_user_by_session_id(db, session_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
	return user
