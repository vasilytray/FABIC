from datetime import datetime, timezone
from fastapi import Request, Depends, Response, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dao import UsersDAO
from app.auth.models import User
from app.config import settings
from app.dependencies.dao_dep import get_session_without_commit
from app.exceptions import (
    TokenNoFound, NoJwtException, TokenExpiredException, NoUserIdException, ForbiddenException, UserNotFoundException
)
from app.auth.utils import set_tokens  # Предполагается импорт функции set_tokens


def get_access_token(request: Request) -> str:
    """Извлекаем access_token из кук."""
    token = request.cookies.get('user_access_token')
    if not token:
        raise TokenNoFound
    return token


def get_refresh_token(request: Request) -> str:
    """Извлекаем refresh_token из кук."""
    token = request.cookies.get('user_refresh_token')
    if not token:
        raise TokenNoFound
    return token


async def check_refresh_token(
        token: str,
        session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    """Проверяем refresh_token и возвращаем пользователя."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise NoJwtException

        user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
        if not user:
            raise NoJwtException

        return user
    except JWTError:
        raise NoJwtException


async def get_current_user(
        request: Request,
        response: Response,
        token: str = Depends(get_access_token),
        session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    """Проверяем access_token, при истечении срока используем refresh_token для обновления."""
    try:
        # Декодируем access токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        # Пытаемся обновить токены через refresh
        try:
            refresh_token = get_refresh_token(request)
            user = await check_refresh_token(refresh_token, session)
            set_tokens(response, user.id)
            return user
        except Exception:
            raise TokenExpiredException
    except JWTError:
        raise NoJwtException

    # Проверяем срок действия access токена
    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        try:
            refresh_token = get_refresh_token(request)
            user = await check_refresh_token(refresh_token, session)
            set_tokens(response, user.id)
            return user
        except Exception:
            raise TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException

    user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
    if not user:
        raise UserNotFoundException
    return user

async def get_current_verified_user(user: User = Depends(get_current_user)):
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяем права администратора."""
    if current_user.role.id in [3, 4]:
        return current_user
    raise ForbiddenException