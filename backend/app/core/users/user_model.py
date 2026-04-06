from ampf.auth.auth_model import AuthUser
from core.roles import Role
from pydantic import BaseModel, EmailStr, Field


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
    password: str | None = Field(None, exclude=True)

    @classmethod
    def create_from_db(cls, user_in_db: "UserInDB") -> "User":
        return cls(**user_in_db.model_dump(exclude={"password"}))

    def to_db(self) -> "UserInDB":
        if not self.email:
            raise ValueError("Email is required")
        user_dict = self.model_dump()
        user_dict["password"] = self.password
        user_dict["email"] = user_dict["email"].lower()

        return UserInDB(**user_dict)


class UserInDB(AuthUser):
    pass
