# app/repositories/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic

T = TypeVar("T")


class AbstractBaseRepository(Generic[T]):
    async def get_by_id(self, obj_id: int) -> T | None:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> T | None:
        raise NotImplementedError

    async def add(self, obj: T) -> T:
        raise NotImplementedError

    async def delete(self, obj: T) -> None:
        raise NotImplementedError


class BaseRepository(AbstractBaseRepository, Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_by_id(self, obj_id: int) -> T | None:
        result = await self.db.execute(select(self.model).filter(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> T | None:
        result = await self.db.execute(select(self.model).filter(self.model.email == email))
        return result.scalar_one_or_none()

    async def add(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.commit()
