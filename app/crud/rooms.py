from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import joinedload, Session

from app.crud.users import get_user_by_id
from app.models.rooms import Room, RoomUser


def create_room(db: Session, name: str, owner_id: int) -> Room | None:
	if get_user_by_id(db, owner_id):
		new_room = Room(name=name, owner_id=owner_id)
		room_user = RoomUser(user_id=owner_id, role="owner")
		new_room.users.append(room_user)
		db.add(new_room)
		db.commit()
		db.refresh(new_room)
		return new_room
	return None


def get_room(db: Session, room_id: int) -> Room | None:
	return db.query(Room).filter(Room.id == room_id).first()


def add_user_to_room(db: Session, room_id: int, user_id: int, role: str = "viewer") -> Room | None:
	room = get_room(db, room_id)
	if room:
		user_in_room = db.query(RoomUser).filter(
			and_(
				RoomUser.room_id == room_id,
				RoomUser.user_id == user_id
			)
		).first()
		if not user_in_room:
			room_user = RoomUser(
				user_id=user_id,
				role=role
			)
			room.users.append(room_user)
			db.commit()
			db.refresh(room)
		return room
	return None


def delete_room(db: Session, room_id: int) -> bool:
	room = get_room(db, room_id)
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
		.options(joinedload(Room.users))
		.all()
	)
	return user_rooms
