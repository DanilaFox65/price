import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from jose import jwt, JWTError
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from core.session import get_db, get_settings
from core.settings import AppSettings
from database.models import User
from src.dependencies.authentication import get_token_payload, get_current_user, security
from src.user.auth import create_refresh_token, create_access_token
from src.user.schemas import UserOut, UserIn, TokenResponse, UserUpdate

router = APIRouter()


@router.post(
  '/user/registration',
  response_model=UserOut.Create,
  description="Регистрация нового пользователя системы.",
  summary="Регистрация нового пользователя системы.",
  responses={
    200: {"description": "Пользователь создан"},
    400: {
      "description": "Ошибка валидации данных",
    },
    500: {
      "description": "Ошибка создания пользователя",
    },
  }
)
async def register(
        user: UserIn.Create,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> UserOut.Create:
  user_data = user.dict()
  existing_user = (await db_connect.execute(
    select(User).filter(User.username == user_data["username"])
  )).scalar()

  if existing_user:
    raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

  user_add = User(
    username=user_data["username"],
    password_hash=hashlib.sha256(user_data["password"].encode()).hexdigest(),
    phone=user_data["phone"]
  )
  db_connect.add(user_add)
  await db_connect.flush()
  await db_connect.refresh(user_add)
  user_add.refresh_token = create_refresh_token(user_add.id, settings=settings)
  return UserOut.Create(
    created_at=user_add.created_at,
    updated_at=user_add.updated_at,
    deleted_at=user_add.deleted_at,
    id=user_add.id,
    username=user_add.username,
    phone=user_add.phone,
  )


@router.post(
  '/user/login',
  response_model=TokenResponse,
  description="Авторизация пользователя.",
  summary="Авторизация пользователя.",
  responses={
    200: {"description": "Успешная авторизация"},
    400: {
      "description": "Ошибка валидации данных",
    },
    404: {
      "description": "Пользователь не найден",
    },
    500: {
      "description": "Ошибка авторизации",
    },
  }
)
async def login(
        user_in: UserIn.Login,
        response: Response,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> TokenResponse:
  user_data = user_in.dict()
  password_hash = hashlib.sha256(user_data["password"].encode()).hexdigest()
  user = (
    await db_connect.execute(
      select(User).filter(
        and_(
          User.password_hash == password_hash,
          User.username == user_data["username"]
        )
      )
    )
  ).scalar()
  if not user:
    raise HTTPException(status_code=404, detail="Пользователь не найден")
  access_token = create_access_token(user.id, settings=settings)
  user.refresh_token = create_refresh_token(user.id, settings=settings)
  response.set_cookie(
    key='refresh_token',
    value=user.refresh_token,
    httponly=True,
    max_age=3600,
    secure=True,
    samesite='Lax',
  )
  if access_token:
    return TokenResponse(
      user_id=user.id,
      username=user.username,
      access_token=access_token,
      refresh_token=user.refresh_token,
      token_type='bearer'
    )


@router.post(
  "/user/me",
  dependencies=[Depends(get_token_payload)]
)
async def me(
        current_user: User = Depends(get_current_user)
):
  return UserOut.Me(
    created_at=current_user.created_at,
    updated_at=current_user.updated_at,
    deleted_at=current_user.deleted_at,
    id=current_user.id,
    username=current_user.username,
    phone=current_user.phone,
    refresh_token=current_user.refresh_token,
  )


@router.post(
  "/user/refresh",
  description="Обновление токена доступа.",
  summary="Обновление токена доступа.",
  response_model=TokenResponse,
  responses={
    200: {"description": "Успешное обновление токена"},
    400: {
      "description": "Ошибка валидации данных",
    },
    401: {
      "description": "Невалидный refresh token",
    },
    500: {
      "description": "Ошибка обновления токена",
    },
  }
)
async def refresh(
        response: Response,
        request: Request,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> TokenResponse:
  refresh_token = request.cookies.get("refresh_token")
  if not refresh_token:
    raise HTTPException(status_code=401, detail="Невалидный refresh token")
  try:
    payload = jwt.decode(refresh_token, settings.jwt_key, algorithms=settings.jwt_algorithm)
    user = (await db_connect.execute(select(User).filter(User.id == payload.get("user_id")))).scalar()
    if not user:
      raise HTTPException(status_code=401, detail="Невалидный refresh token")
    new_access_token = create_access_token(user.id, settings=settings)
    new_refresh_token = create_refresh_token(user.id, settings=settings)
    user.refresh_token = new_refresh_token
    response.set_cookie(
      key='refresh_token',
      value=user.refresh_token,
      httponly=True,
      max_age=3600,
      secure=True,
      samesite='Lax',
    )
    return TokenResponse(
      user_id=user.id,
      username=user.username,
      access_token=new_access_token,
      refresh_token=user.refresh_token,
      token_type='bearer'
    )
  except JWTError:
    raise HTTPException(status_code=401, detail="Невалидный refresh token")


# Мягкое удаление пользователя
@router.delete("/user/{user_id}")
async def delete_user(
        user_id: int,
        db_connect: AsyncSession = Depends(get_db)
) -> JSONResponse:

  user = await db_connect.get(User, user_id)


  if not user:
    raise HTTPException(status_code=404, detail="Пользователь не найден")


  if user.deleted_at is not None:
    raise HTTPException(status_code=400, detail="Пользователь уже удалён")


  user.deleted_at = datetime.now()

  # Сохраняем изменения в базе данных
  await db_connect.commit()

  return JSONResponse(
    status_code=200,
    content={}
  )

@router.post(
    "/user/change_data",
    description="Изменение данных существующего пользователя",
    summary="Изменение данных существующего пользователя",
    responses={
        200: {"description": "Данные успешно изменены!"},
        500: {"description": "Данные изменить не удалось"}
    }
)
async def change_data(
        id: int,
        user_update: UserUpdate,
        db_connect: AsyncSession = Depends(get_db),
):
    user_data: User = (await db_connect.execute(select(User).filter(User.id == id))).scalar()
    if not user_data:
        return HTTPException(status_code=404, detail="Пользователь не найден!")
    else:
        if user_update.username != "string":
            user_data.username = user_update.username

        if user_update.password != "string":
            user_data.password_hash = hashlib.sha256(user_update.password.encode()).hexdigest()

        if user_update.phone != "string":
            user_data.phone = user_update.phone

            user_data.update_at = datetime.now()

            await db_connect.commit()
            await db_connect.refresh(user_data)

            return {"message": "Данные пользователя успешно изменены!"}


@router.post(
  "/user/delete_user",
  description="Удаление пользователя из базы данных",
  summary="Удаление пользователей из базы данных",
  responses={
    200: {"description": "Пользователь успешно удалён"},
    404: {"description": "Пользователь с таким id не найден или уже удалён"},
    500: {"description": "Ошибка сервера"}
  }
)
async def delete_user(
        id: int,
        db_connect: AsyncSession = Depends(get_db),
):
  # Поиск пользователя в базе данных
  user_data: User = (await db_connect.execute(
    select(User).filter(User.id == id, User.deleted_at.is_(None))
  )).scalar_one_or_none()  # Используем scalar_one_or_none для обработки случая, когда пользователь не найден

  if not user_data:
    raise HTTPException(status_code=404, detail="Пользователь с таким id не найден или уже удалён")

  # Удаляем пользователя
  user_data.deleted_at = datetime.now()

  # Сохраняем изменения в базе данных
  await db_connect.commit()  # Вызов коммита для сохранения изменений

  return {"message": "Пользователь успешно удалён!"}










