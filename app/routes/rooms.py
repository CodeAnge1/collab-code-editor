from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.crud import rooms
from app.db import get_session
from app.models import User
from app.schemas.rooms import RoomInfo, RoomCreate
from app.utils import get_current_user

router = APIRouter(
	prefix="/rooms",
	tags=["rooms"]
)


@router.get("/", response_model=List[RoomInfo])
def get_user_rooms(db: Session = Depends(get_session), cur_user: User = Depends(get_current_user)):
	user_rooms = rooms.get_user_rooms(db, cur_user.id)
	return [RoomInfo.model_validate(room) for room in user_rooms] if user_rooms else []


@router.post("/", response_model=RoomInfo)
def create_room(room_data: RoomCreate, db: Session = Depends(get_session), cur_user: User = Depends(get_current_user)):
	room = rooms.create_room(db, room_data, cur_user.id)
	if not room:
		raise HTTPException(status_code=400, detail="Failed to create room")
	return RoomInfo.model_validate(room)


@router.get("/{room_id}", response_model=RoomInfo)
def get_room(room_id: str, db: Session = Depends(get_session), cur_user: User = Depends(get_current_user)):
	room = rooms.get_room(db, room_id, cur_user.id)
	if not room:
		raise HTTPException(status_code=404, detail="Room not found")
	return RoomInfo.model_validate(room)


@router.post("{room_id}/join", response_model=RoomInfo)
def join_room(room_id: str, password: str | None = Body(..., embed=True), db: Session = Depends(get_session),
			  cur_user: User = Depends(get_current_user)):
	room = rooms.add_user_to_room(db, room_id, cur_user.id, password)
	if not room:
		raise HTTPException(status_code=403, detail="Invalid password or access denied")
	return RoomInfo.model_validate(room)


@router.delete("/{room_id}")
def delete_room(room_id: str, db: Session = Depends(get_session), cur_user: User = Depends(get_current_user)):
	room = rooms.get_room(db, room_id, cur_user.id)
	if not room:
		raise HTTPException(status_code=404, detail="Room not found")
	if room.owner_id != cur_user.id:
		raise HTTPException(status_code=403, detail="Not authorized")
	status = rooms.delete_room(db, room_id, cur_user.id)
	return {"success": status}
