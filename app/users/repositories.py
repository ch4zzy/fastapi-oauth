# app/repositories/user.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import SecurityService
from app.repositories.base import BaseRepository
from app.users.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def create_user(self, email: str, password: str) -> User:
        user = User(email=email, password=SecurityService.get_password_hash(password))
        if await self.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        return await self.add(user)
