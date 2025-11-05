from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..models.base import Base

engine = create_engine(
	url=settings.db_cfg.get_url(),
	echo=settings.db_cfg.use_logging,
	pool_size=settings.db_cfg.pool_size,
	max_overflow=settings.db_cfg.max_overflow,
)

session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def create_tables():
	Base.metadata.create_all(engine)


def get_session():
	session = session_factory()
	try:
		yield session
	finally:
		session.close()
