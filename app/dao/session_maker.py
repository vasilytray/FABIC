from dishka import Provider, provide, Scope
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError


class DatabaseSessionManager(Provider):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_maker = session_maker

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncSession:
        async with self.session_maker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                logger.error(f"Ошибка SQLAlchemy при использовании сессии: {e}")
                await session.rollback()
                raise
            except Exception as e:
                logger.error(f"Неожиданная ошибка при использовании сессии: {e}")
                raise