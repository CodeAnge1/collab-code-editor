"""change room id to uuid and add room type and password

Revision ID: 5026097f0e93
Revises: 82e44e1a9bfd
Create Date: 2025-12-11 23:50:01.653100

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5026097f0e93"
down_revision: Union[str, Sequence[str], None] = "82e44e1a9bfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.execute("CREATE TYPE room_type AS ENUM ('PUBLIC', 'PRIVATE')")
	op.add_column(
		"rooms",
		sa.Column(
			"type",
			sa.Enum("PUBLIC", "PRIVATE", name="room_type"),
			server_default="PUBLIC",
			nullable=False,
		),
	)
	op.add_column(
		"rooms", sa.Column("hashed_password", sa.String(), nullable=True)
	)

	op.add_column(
		"rooms",
		sa.Column(
			"room_uuid",
			sa.UUID(as_uuid=True),
			server_default=sa.text("gen_random_uuid()"),
			nullable=True
		)
	)
	op.add_column(
		"room_users",
		sa.Column(
			"room_uuid",
			sa.UUID(as_uuid=True),
			server_default=sa.text("gen_random_uuid()"),
			nullable=False,
		)
	)
	op.execute("UPDATE rooms SET room_uuid=gen_random_uuid()")
	op.execute("UPDATE room_users "
			   "SET room_uuid = rooms.room_uuid "
			   "FROM rooms "
			   "WHERE room_users.room_id = rooms.id")
	op.alter_column("rooms", "room_uuid", nullable=False)

	op.drop_constraint("room_users_room_id_fkey", "room_users")

	op.drop_constraint("rooms_pkey", "rooms")
	op.create_primary_key("rooms_pkey", "rooms", ["room_uuid"])
	op.drop_column("rooms", "id")
	op.alter_column("rooms", "room_uuid", new_column_name="id")

	op.drop_column("room_users", "room_id")
	op.alter_column("room_users", "room_uuid", new_column_name="room_id")

	op.create_foreign_key(
		"room_users_room_id_fkey",
		"room_users",
		"rooms",
		["room_id"],
		["id"],
		ondelete="CASCADE",
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_column("rooms", "hashed_password")
	op.drop_column("rooms", "type")
	op.execute("DROP TYPE IF EXISTS room_type")

	op.add_column(
		"rooms",
		sa.Column(
			"old_id",
			sa.Integer(),
			autoincrement=True,
		)
	)
	op.add_column(
		"room_users",
		sa.Column(
			"old_room_id",
			sa.Integer(),
			nullable=True,
		)
	)
	op.execute("UPDATE rooms SET old_id = seq.row_num "
			   "FROM (SELECT id, row_number() OVER (ORDER BY created_at) as row_num FROM rooms) seq "
			   "WHERE rooms.id = seq.id")
	op.execute("UPDATE room_users "
			   "SET old_room_id = rooms.old_id "
			   "FROM rooms "
			   "WHERE room_users.room_id = rooms.id")

	op.drop_constraint("room_users_room_id_fkey", "room_users")
	op.drop_constraint("rooms_pkey", "rooms")

	op.create_primary_key("rooms_pkey", "rooms", ["old_id"])

	op.drop_column("rooms", "id")
	op.alter_column("rooms", "old_id", new_column_name="id", nullable=False)
	op.drop_column("room_users", "room_id")
	op.alter_column("room_users", "old_room_id", new_column_name="room_id")

	op.create_foreign_key(
		"room_users_room_id_fkey",
		"room_users",
		"rooms",
		["room_id"],
		["id"],
		ondelete="CASCADE",
	)
