from typing import AsyncGenerator
from dishka import Provider, provide
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.dao.database import async_session_maker


class DatabaseSessionManager(Provider):
    """
    Класс для управления асинхронными сессиями базы данных с использованием Dishka.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_maker = session_maker

    @provide
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Предоставляет новую сессию базы данных.
        """
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Ошибка при использовании сессии базы данных: {e}")
                raise
            finally:
                await session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Здесь можно добавить логику для очистки ресурсов, если необходимо
        pass


# Инициализация менеджера сессий базы данных
session_manager = DatabaseSessionManager(async_session_maker)
