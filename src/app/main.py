from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.app.routes.blog import router as blog_router
from src.app.routes.users import router as auth_router
from src.app.routes.main_pages import router as main_pages_router
from src.app.routes.activate_and_reset import router as mail_router
from src.app.back.users_back import get_name_and_login_from_decrypt_token


templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="templates")

app.include_router(router=blog_router, prefix="/blog")
app.include_router(router=auth_router)
app.include_router(router=main_pages_router)
app.include_router(router=mail_router, prefix="/auth")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """Начальная страница"""
    name, login = get_name_and_login_from_decrypt_token(request)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "login": login,
                                                     "name": name})