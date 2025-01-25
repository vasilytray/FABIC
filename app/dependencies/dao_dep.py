from typing import AsyncGenerator
from fastapi import Depends
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dao import UsersDAO, RoleDAO
from app.dao.database import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает и автоматически управляет асинхронной сессией базы данных."""
    async with async_session_maker() as session:
        try:
            yield session
        except (SQLAlchemyError, Exception) as e:
            # Логирование всех критических ошибок базы данных
            logger.error(f"Критическая ошибка сессии базы данных: {e}")
            # Откат транзакции при возникновении ошибки
            await session.rollback()
            raise
        finally:
            # Гарантированное закрытие сессии
            await session.close()


async def get_users_dao(
        session: AsyncSession = Depends(get_async_session)
) -> UsersDAO:
    """Зависимость для создания DAO пользователей."""
    return UsersDAO(session)


async def get_role_dao(
        session: AsyncSession = Depends(get_async_session)
) -> RoleDAO:
    """Зависимость для создания DAO ролей."""
    return RoleDAO(session)