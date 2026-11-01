from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Фабрика сессий для работы с БД
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор зависимостей (Dependency) FastAPI для получения сессии БД."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
