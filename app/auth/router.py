from typing import List
from fastapi import APIRouter, Response, Depends
from app.auth.models import User
from app.auth.utils import authenticate_user, set_tokens
from app.dependencies.auth_dep import get_current_user, get_current_admin_user, check_refresh_token
from app.dependencies.dao_dep import get_users_dao
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from app.auth.dao import UsersDAO
from app.auth.schemas import SUserRegister, SUserAuth, EmailModel, SUserAddDB, SUserInfo

router = APIRouter()


@router.post("/register/")
async def register_user(user_data: SUserRegister, users_dao: UsersDAO = Depends(get_users_dao)) -> dict:
    # Проверка существования пользователя
    existing_user = await users_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    if existing_user:
        raise UserAlreadyExistsException

    # Подготовка данных для добавления
    user_data_dict = user_data.model_dump()
    user_data_dict.pop('confirm_password', None)

    # Добавление пользователя
    await users_dao.add(values=SUserAddDB(**user_data_dict))

    return {'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/")
async def auth_user(
        response: Response,
        user_data: SUserAuth,
        users_dao: UsersDAO = Depends(get_users_dao)
) -> dict:
    user = await users_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email)
    )

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {
        'ok': True,
        'message': 'Авторизация успешна!'
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.get("/all_users/")
async def get_all_users(users_dao: UsersDAO = Depends(get_users_dao),
                        user_data: User = Depends(get_current_admin_user)
                        ) -> List[SUserInfo]:
    return await users_dao.find_all()


@router.post("/refresh")
async def process_refresh_token(
        response: Response,
        user: User = Depends(check_refresh_token)
):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
