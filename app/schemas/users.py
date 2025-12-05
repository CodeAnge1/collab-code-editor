from typing import Annotated

from pydantic import BaseModel, BeforeValidator, EmailStr, Field


def strip_and_lower(v: object) -> str | None:
	return str(v).strip().lower() if v else None


email_type = Annotated[EmailStr, BeforeValidator(strip_and_lower)]
username_type = Annotated[str, Field(pattern=r"^\w+$", min_length=5, max_length=40)]


class UserAdd(BaseModel):
	username: username_type
	email: email_type
	password: str


class UserLogin(BaseModel):
	username_or_email: email_type | username_type
	password: str


class UserInfo(BaseModel):
	id: int
	username: str
	email: EmailStr
