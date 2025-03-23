# app/users/services.py
from typing import Optional

from app.repositories.user import UserRepository
from app.users.models import User
from app.users.schemas import UserResponse
from app.auth.security import SecurityService


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, email: str, password: str) -> UserResponse:
        hashed_password = SecurityService.get_password_hash(password)
        user = await self.repo.create_user(email, hashed_password)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> Optional[User]:
        user = await self.repo.get_by_email(email)
        return await self.repo.get_by_email(email)