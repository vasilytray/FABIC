from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from dishka import make_async_container
from app.auth.router import router as router_auth
from app.dao.database import async_session_maker
from app.dao.session_maker import DatabaseSessionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем контейнер при старте приложения
    container = make_async_container(
        DatabaseSessionManager(async_session_maker),
        FastapiProvider()
    )

    # Устанавливаем dishka для FastAPI
    setup_dishka(container=container, app=app)

    yield

    # Закрываем контейнер при завершении работы приложения
    await container.close()


# Создаем FastAPI приложение с кастомным жизненным циклом
app = FastAPI(
    lifespan=lifespan,
    title="Your Application",
    description="Application description"
)

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Монтируем статические файлы
app.mount('/static', StaticFiles(directory='app/static'), name='static')


# Корневой эндпоинт
@app.get("/")
def home_page():
    return {
        "message": "Добро пожаловать! Пусть эта заготовка станет удобным инструментом для вашей работы и "
                   "приносит вам пользу!"
    }


# Подключаем роутеры
app.include_router(router_auth)
