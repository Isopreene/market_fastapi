from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.app.back.mail_back import MailCache
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.back.users_back import create_access_token
from src.database.connection import get_db
from src.database.models import User as UserModel
from sqlalchemy import select
from typing import Annotated
from src.app.back.users_back import (get_params_from_decrypt_token,
                                     get_password_hash)


templates = Jinja2Templates(directory="templates")
router = APIRouter()
router.mount("/static", StaticFiles(directory="templates"), name="templates")
mail_cache = MailCache()


@router.get("/activate_link")
async def activate_link(request: Request,
                        secret_key: str,
                        db: AsyncSession = Depends(get_db)):
    link = mail_cache.activate_link(secret_key)
    if link:
        user = await db.execute(select(UserModel).filter_by(email=link.email))
        user = user.scalar()
        if user:
            user.activated = True
            await db.commit()
        else:
            return Response(status_code=404, content="Пользователь не "
                                                     "зарегистрирован")
        return templates.TemplateResponse(
            "users/registration/mail_confirmed.html",
            context={"request": request})
    else:
        return Response(status_code=404, content="Неверная ссылка")


@router.get("/new_password")
async def get_new_password(request: Request, secret_key: str):
    link = mail_cache.activate_link(secret_key)
    if link:
        response = templates.TemplateResponse(
            "users/recovery/new_password.html", {"request": request})
        access_token = create_access_token({"email": link.email})
        response.set_cookie(key="access_token", value=access_token)
        response.set_cookie(key="token_type", value="bearer")
        return response
    return Response(status_code=404, content="Неверная ссылка")


@router.post("/new_password")
async def post_new_password(request: Request,
                            password: Annotated[str, Form(...)],
                            repeat_password: Annotated[str, Form(...)],
                            db: AsyncSession = Depends(get_db)):
    """ставит новый пароль, полученный из формы. С защитой от POST-запросов"""
    token = request.cookies.get("access_token")
    token_type = request.cookies.get("token_type")
    if token_type != "bearer" or not token:
        return Response(status_code=404, content="Ссылка на смену пароля не "
                                                 "активирована")
    email = get_params_from_decrypt_token(token).get("email")
    if not password == repeat_password:
        return Response(status_code=404, content="Пароли не совпадают")
    if not email:
        return Response(status_code=404, content="Вы пытаетесь поменять "
                                                 "пароль без запроса "
                                                 "активационной ссылки?")
    user = await db.execute(
        select(UserModel).filter_by(email=email))
    user = user.scalar()
    if user:
        user.hashed_password = get_password_hash(password)
        await db.commit()
        return templates.TemplateResponse(
            "users/recovery/new_password_updated.html", context={
                "request": request})
