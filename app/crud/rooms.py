from typing import List
from uuid import UUID

from sqlalchemy.orm import selectinload, Session

from app.crud.users import get_user_by_id
from app.models.rooms import Room, RoomUser
from app.schemas.rooms import RoomCreate, RoomType
from app.utils import get_password_hash, verify_password


def user_in_room(db: Session, room_id: str, user_id: int) -> bool:
	return db.query(RoomUser).filter(
		RoomUser.room_id == UUID(room_id),
		RoomUser.user_id == user_id
	).first() is not None


def create_room(db: Session, room: RoomCreate, owner_id: int) -> Room | None:
	if get_user_by_id(db, owner_id):
		new_room = Room(
			name=room.name,
			owner_id=owner_id,
			type=room.type,
			hashed_password=get_password_hash(room.password) if room.type == RoomType.PRIVATE else None
		)
		room_user = RoomUser(user_id=owner_id, role="owner")
		new_room.users.append(room_user)
		db.add(new_room)
		db.commit()
		db.refresh(new_room)
		return new_room
	return None


def get_room(db: Session, room_id: str, user_id: int) -> Room | None:
	room = db.query(Room).filter(Room.id == UUID(room_id)).options(selectinload(Room.users)).first()
	if room.type == RoomType.PUBLIC:
		return room
	return room if room and any(user.user_id == user_id for user in room.users) else None


def add_user_to_room(db: Session, room_id: str, user_id: int, password: str | None = None,
					 role: str = "viewer") -> Room | None:
	room = get_room(db, room_id, user_id)
	if not room:
		return None
	if user_in_room(db, room_id, user_id):
		return room
	if room.type == RoomType.PRIVATE:
		if not password or not verify_password(password, room.hashed_password):
			return None
	room_user = RoomUser(
		user_id=user_id,
		role=role
	)
	room.users.append(room_user)
	db.commit()
	db.refresh(room)
	return room


def delete_room(db: Session, room_id: str, user_id: int) -> bool:
	room = db.query(Room).filter(Room.id == UUID(room_id), Room.owner_id == user_id).first()
	if room:
		db.delete(room)
		db.commit()
		return True
	return False


def get_user_rooms(db: Session, user_id: int) -> List[Room]:
	user_rooms = (
		db.query(Room)
		.join(RoomUser, Room.id == RoomUser.room_id)
		.filter(RoomUser.user_id == user_id)
		.all()
	)
	return user_rooms
