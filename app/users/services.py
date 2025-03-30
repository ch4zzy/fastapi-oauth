# app/users/services.py
from typing import Optional

from app.users.repositories import UserRepository
from app.users.models import User
from app.users.schemas import UserResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, email: str, password: str) -> UserResponse:
        user = await self.repo.create_user(email, password)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repo.get_by_email(email)