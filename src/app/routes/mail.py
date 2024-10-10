from fastapi import APIRouter, Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from starlette.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from src.app.routes.back.mail_back import MailCache
from src.schemas.mail import EmailSchema
from src.celery_mail.celery_config import celery_app
from dotenv import load_dotenv

templates = Jinja2Templates(directory="templates")
router = APIRouter()
router.mount("/static", StaticFiles(directory="templates"), name="templates")
mail_cache = MailCache()
load_dotenv(".env")

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_PORT=os.environ.get("MAIL_PORT"),
    MAIL_SERVER=os.environ.get("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

@celery_app.task
async def send_email(request: Request, email:str):
    url = mail_cache.generate_link()
    template = f"""
    <html>
        <body>
            <p>
                Ваша ссылка для активации аккаунта: { url }
            </p>
        </body>
    </html>
    """
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email,],
        body=template,
        subtype="html"
   )
    fm = FastMail(conf)
    res = await fm.send_message(message)
    return res

@router.get("/activate_link")
async def activate_link(request: Request, secret_key:str):
    activate = mail_cache.activate_link(secret_key)
    if activate:
        return templates.TemplateResponse("mail/mail_confirmed.html", context={
            "request": request})
    else:
        return Response(status_code=404, content="Неверная ссылка")

