from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.app.routes.blog import router as blog_router
from src.app.routes.auth import router as auth_router
from src.app.routes.main_pages import router as main_pages_router
from src.app.routes.mail import router as mail_router
from base64 import b64decode
from celery import Celery
import os

templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="templates")

app.include_router(router=blog_router, prefix="/blog")
app.include_router(router=auth_router)
app.include_router(router=main_pages_router)
app.include_router(router=mail_router)

CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL",
                                        "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")
celery_app = Celery(__name__,
                    broker=CELERY_BROKER_URL,
                    backend=CELERY_RESULT_BACKEND)



@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """Начальная страница"""
    login = request.cookies.get("login", False)
    name = b64decode(request.cookies.get("name", "").encode("utf-8")).decode()
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "login": login,
                                                     "name": name})
