from fastapi import Request, APIRouter, Depends, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.database.connection import get_db
from src.database.models import User as UserModel
from src.schemas.users import UserReg, UserLogin, UserRecover
from datetime import datetime
from typing import Annotated
from src.app.routes.back.auth_back import (get_password_hash,
                                           create_access_token,
                                           verify_password_hash)
from .mail import send_email
from base64 import b64encode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="templates"), name="templates")


@router.get("/register", response_model=UserReg)
async def register(request: Request):
    return templates.TemplateResponse("auth/registration.html", {"request":
                                                                request},
                                      status_code=302)

@router.post("/register", response_class=RedirectResponse,)
async def user_register(name: Annotated[str, Form(...)],
                    email: Annotated[str, Form(...)],
                    password: Annotated[str, Form(...)],
                    repeat_password: Annotated[str, Form(...)],
                    phone: Annotated[str, Form(...)],
                    db: AsyncSession = Depends(get_db),
                    ):
    emails = await db.execute(select(UserModel).filter_by(email=email))
    emails = emails.scalars().all()
    if email in emails:
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
    res = await send_email(email=email)
    return RedirectResponse(url=f"/send_mail/?email={email}", status_code=307)


@router.get('/login', response_model=UserLogin)
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post('/login', response_class=RedirectResponse)
async def user_login(
               email: Annotated[str, Form(...)],
               password: Annotated[str, Form(...)],
               db: AsyncSession=Depends(get_db)):
    user = await db.execute(select(UserModel).filter_by(email=email))
    user = user.scalar()
    if not user.email or not verify_password_hash(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email "
                                                    "or password")
    access_token = create_access_token({"email": user.email})
    response = RedirectResponse(url="/", status_code=302)

    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="token_type", value="bearer")
    response.set_cookie(key="login", value="True")
    response.set_cookie(key="name", value=b64encode(user.name.encode('utf-8')
    ).decode())
    return response

@router.get('/recover', response_model=UserRecover)
async def recover(request: Request):
    return templates.TemplateResponse("auth/recover.html", {"request": request})

@router.post('/recover', response_class=HTMLResponse)
async def user_recover(request: Request, email: Annotated[str, Form(...)],
               db: AsyncSession=Depends(get_db)):
    emails = await db.execute(select(UserModel).filter_by(email=email))
    emails = emails.scalars().all()
    if email in emails:
        ... # брокер
        return templates.TemplateResponse("auth/email_sent.html",
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