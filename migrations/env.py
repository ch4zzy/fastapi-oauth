import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncConnection
from alembic import context
from app.users.models import Base as UserBase
from app.core.config import settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = [UserBase.metadata]


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(settings.DATABASE_URL, future=True, poolclass=None)

    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection: AsyncConnection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
