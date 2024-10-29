from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Annotated

from fastapi import Depends
from loguru import logger
from sqlalchemy import func, TIMESTAMP, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from app.config import database_url
from typing import AsyncGenerator

engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


@asynccontextmanager
async def managed_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with managed_session() as session:
        yield session


# Dependency для использования в маршрутах FastAPI
SessionDep = Depends(get_session)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Базовый класс будет абстрактным, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> Dict[str, Any]:
        # Метод для преобразования объекта в словарь
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
