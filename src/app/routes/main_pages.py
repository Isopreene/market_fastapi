from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="templates"), name="templates")

@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    """Раздел FAQ"""
    return templates.TemplateResponse("faq.html", {"request": request})

@router.get("/pay_return", response_class=HTMLResponse)
async def pay_return(request: Request):
    """Раздел Оплата и возврат"""
    return templates.TemplateResponse("pay_return.html", {"request": request})

@router.get("/tariffs", response_class=HTMLResponse)
async def tariffs(request: Request):
    """Раздел тарифов. Информацию хранить в другом месте, здесь для теста"""
    tariffs_list = [
        {"name": "Базовый", "price": 4000, "description": "блаблабла"},
        {"name": "Расширенный", "price": 16000, "description": "другое "
                                                               "блаблабла"} ,
        {"name": "Элитный", "price": 35000, "description": "третье блаблабла"}]

    durations_list = [
        {"description": "1 месяц", "duration":1, "discount": 0},
        {"description": "3 месяца (скидка 10%)", "duration":3, "discount": 10},
        {"description": "6 месяцев (скидка 30%)", "duration":6, "discount":
            30},
    ]
    return templates.TemplateResponse("tariffs.html", {"request": request,
                                                       "tariffs_list": tariffs_list,
                                                       "durations_list": durations_list})