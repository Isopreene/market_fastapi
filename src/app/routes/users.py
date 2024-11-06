from fastapi import Request, APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.database.connection import get_db
from src.database.models import User as UserModel
from src.schemas.users import UserReg, UserLogin, UserRecover
from datetime import datetime
from src.app.back.users_back import (get_password_hash,
                                     create_access_token,
                                     verify_password_hash
                                     )
from src.celery_mail.tasks import send_email
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated


router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="templates"), name="templates")


@router.get("/register", response_model=UserReg)
async def get_register(request: Request):
    return templates.TemplateResponse("users/registration/register.html",
                                      {"request": request},
                                      status_code=200)


@router.post("/register", response_class=RedirectResponse,)
async def post_register(request: Request,
                        name: Annotated[str, Form(...)],
                        email: Annotated[str, Form(...)],
                        password: Annotated[str, Form(...)],
                        repeat_password: Annotated[str, Form(...)],
                        phone: Annotated[str, Form(...)],
                        db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(UserModel).filter_by(email=email))
    user = user.scalar()
    if user and email == user.email:
        raise HTTPException(detail="Email already registered", status_code=400)
    if password != repeat_password:
        raise HTTPException(detail="Passwords do not match", status_code=400)
    reg = UserModel(name=name,
                    email=email,
                    phone=phone,
                    hashed_password=get_password_hash(password),
                    added_at=datetime.now())
    db.add(reg)
    await db.commit()
    await db.refresh(reg)
    await send_email(email=email, route="activate_link")
    return templates.TemplateResponse("users/registration/mail_sent.html",
                                      {"request": request})


@router.get('/login', response_model=UserLogin)
async def get_login(request: Request):
    return templates.TemplateResponse("users/auth/login.html", {"request":
                                                                request})


@router.post('/login', response_class=RedirectResponse)
async def post_login(
               email: Annotated[str, Form(...)],
               password: Annotated[str, Form(...)],
               db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(UserModel).filter_by(email=email))
    user = user.scalar()
    if (not user or
            not user.email or
            not verify_password_hash(password, user.hashed_password)):
        raise HTTPException(status_code=401,
                            detail="Incorrect email or password")
    if not user.activated:
        raise HTTPException(status_code=401, detail="User is not activated")
    access_token = create_access_token({"name": user.name,
                                        "email": user.email,
                                        "login": True})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="token_type", value="bearer")
    return response


@router.get('/recover', response_model=UserRecover)
async def get_recover(request: Request):
    return templates.TemplateResponse("users/recovery/recover.html",
                                      {"request": request})


@router.post('/recover', response_class=HTMLResponse)
async def post_recover(request: Request, email: Annotated[str, Form(...)],
                       db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(UserModel).filter_by(email=email))
    user = user.scalar()
    if user.email == email:
        await send_email(email=email, route="new_password")
        return templates.TemplateResponse("users/recovery/email_sent.html",
                                          {"request": request})
    else:
        raise HTTPException(status_code=401, detail="Email not registered")


@router.get('/logout', response_class=RedirectResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="token_type")
    response.delete_cookie(key="login")
    response.delete_cookie(key="name")
    return response
