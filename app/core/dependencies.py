# app/core/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


from app.database import get_db
from app.repositories.user import UserRepository
from app.users.services import UserService


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)


