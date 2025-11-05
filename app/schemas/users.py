from typing import Annotated

from pydantic import BaseModel, BeforeValidator, EmailStr, model_validator


def strip_and_lower(v: object) -> str | None:
	return str(v).strip().lower() if v else None


email_type = Annotated[EmailStr, BeforeValidator(strip_and_lower)]


class UserAdd(BaseModel):
	username: str
	email: email_type
	password: str


class UserLogin(BaseModel):
	username: str | None
	email: email_type | None
	password: str

	@model_validator(mode="after")
	def validate_both_not_null(self):
		if self.username is None and self.email is None:
			raise ValueError("At least one of username or email must be provided")
		return self


class UserInfo(BaseModel):
	id: int
	username: str
	email: EmailStr
