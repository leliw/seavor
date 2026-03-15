from typing import Any

from ampf.auth.auth_model import AuthUser
from pydantic import BaseModel, EmailStr, Field, model_serializer

from core.roles import Role


class UserHeader(BaseModel):
    username: str
    email: EmailStr
    name: str | None = None
    disabled: bool = False
    roles: list[Role] = Field(default_factory=list)
    picture: str | None = None


class UserPatch(BaseModel):
    disabled: bool | None = None
    password: str | None = None


class User(UserHeader):
    password: str | None = None

    @classmethod
    def create_from_db(cls, user_in_db: "UserInDB") -> "User":
        return User(**user_in_db.model_dump(exclude={"password"}))

    def to_db(self) -> "UserInDB":
        user_dict = dict(self)
        if user_dict["email"]:
            user_dict["email"] = user_dict["email"].lower()
        else:
            raise ValueError("Email is required")
        user_dict.pop("password")
        return UserInDB(**user_dict)

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        self_dict = dict(self)
        self_dict.pop("password")
        return self_dict


class UserInDB(AuthUser):
    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        self_dict = dict(self)
        self_dict.pop("password")
        return self_dict
