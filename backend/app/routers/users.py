from typing import List

from dependencies import UserServiceDep
from fastapi import APIRouter
from pydantic import BaseModel

from core.users.user_model import User, UserHeader, UserPatch

router = APIRouter(tags=["Users"])


@router.post("")
async def create(user_service: UserServiceDep, user: User):
    await user_service.create(user.to_db())
    return user


@router.get("")
async def get_all(user_service: UserServiceDep) -> List[UserHeader]:
    return await user_service.get_all()


@router.get("/{username}")
async def get(user_service: UserServiceDep, username: str) -> User:
    return User.create_from_db(await user_service.get(username))


@router.put("/{username}")
async def update(user_service: UserServiceDep, username: str, user: User):
    return await user_service.update(username, user.to_db())


class PasswordDTO(BaseModel):
    password: str


@router.patch("/{username}/change-password")
async def change_password(user_service: UserServiceDep, username: str, body: PasswordDTO):
    await user_service.patch(username, UserPatch(password=body.password))


@router.delete("/{username}")
async def delete(user_service: UserServiceDep, username: str):
    await user_service.delete(username)
