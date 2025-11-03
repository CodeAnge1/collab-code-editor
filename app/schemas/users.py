from pydantic import BaseModel, EmailStr


class UserAdd(BaseModel):
	username: str
	email: EmailStr
	password: str


class UserLogin(BaseModel):
	username: str | None
	email: EmailStr | None
	password: str


class UserInfo(BaseModel):
	id: int
	username: str
	email: EmailStr
