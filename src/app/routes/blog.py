from fastapi import Request, APIRouter, Depends, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.database.connection import get_db
from src.database.models import Article as ArticleModel
from src.schemas.blog import Article as ArticleSchema
from sqlalchemy.orm.exc import NoResultFound
from typing import List
from datetime import datetime
from src.app.back.cache import Cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from src.app.back.users_back import get_name_and_login_from_decrypt_token


templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Blog"])
router.mount("/static", StaticFiles(directory="templates"), name="templates")
cache = Cache()


@router.get("/all", response_class=RedirectResponse)
async def all_articles():
    return RedirectResponse(url="/blog/all/1", status_code=302)


@router.get("/all/{page:int}",
            response_class=HTMLResponse,
            response_model=ArticleSchema)
async def all_articles_with_pages(request: Request,
                                  category: str = "",
                                  page: int = 1,
                                  db: AsyncSession = Depends(get_db)):
    """Вернуть по GET-запросу список всех статей. Подключена пагинация.
    Нынешний кэш создан для примера, в продукте заменить на redis """
    name, login = get_name_and_login_from_decrypt_token(request)
    if not cache.articles and not cache.categories:
        categories = await db.execute(select(
            ArticleModel.category).distinct())
        categories = sorted([c[0] for c in categories.all()])
        if category:
            articles = await db.execute(select(ArticleModel).filter_by(
                category=category))
            articles = articles.scalars().all()

        else:
            articles = await db.execute(select(ArticleModel))
            articles = articles.scalars().all()
        cache.articles = articles
        cache.categories = categories
    categories = cache.categories
    # выводим по 12 статей на страницу, можно изменить
    articles = cache.get_articles(limit=12, page=page)
    if category:
        # сортируем статьи из кэша по категории
        articles = [article
                    for article in articles
                    if article.category == category]
    return templates.TemplateResponse("blog/articles.html",
                                      {"request": request,
                                       "login": login,
                                       "name": name,
                                       "articles": articles,
                                       "categories": categories,
                                       "category": category,
                                       "page": page,
                                       "pages_number": cache.pages_number})


@router.post("/all", name="search_articles",
             response_class=HTMLResponse,
             response_model=ArticleSchema)
async def search_articles(request: Request,
                          search_text: str = Form(),
                          db: AsyncSession = Depends(get_db)):
    name, login = get_name_and_login_from_decrypt_token(request)
    categories = await db.execute(select(ArticleModel.category).distinct(
    ))
    categories = sorted([c[0] for c in categories.all()])
    if search_text:
        articles = await db.execute(select(ArticleModel).filter_by(
            ArticleModel.tsvector.match(search_text)))
        articles = articles.scalars().all()
    else:
        articles = await db.execute(select(ArticleModel))
        articles = articles.scalars().all()

    return templates.TemplateResponse("blog/articles.html",
                                      {"request": request,
                                       "login": login,
                                       "name": name,
                                       "articles": articles,
                                       "categories": categories,
                                       "search_text": search_text})


@router.get("/{id_:int}",
            response_class=HTMLResponse,
            response_model=List[ArticleSchema])
async def one_article(id_: int,
                      request: Request,
                      db: AsyncSession = Depends(get_db)):
    name, login = get_name_and_login_from_decrypt_token(request)
    try:
        article = await db.execute(select(ArticleModel).filter_by(id=id_))
        article = article.scalar()
    except NoResultFound:
        return Response(f"Статья с id {id_} не найдена", status_code=404)
    return templates.TemplateResponse("blog/article.html",
                                      {"request": request,
                                       "login": login,
                                       "name": name,
                                       "article": article})


@router.post("/create", response_model=ArticleSchema)
async def post_article(model: ArticleSchema,
                       db: AsyncSession = Depends(get_db)):
    debug = settings.DEBUG
    if not debug:
        return Response(status_code=404, content="Not allowed")
    article = ArticleModel(name=model.name,
                           category=model.category,
                           description=model.description,
                           added_at=datetime.now())
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return RedirectResponse(f"{article.id}", status_code=302)


@router.post("/create_start",
             response_model=ArticleSchema)
async def post_start_articles(
                        db: AsyncSession = Depends(get_db)):
    debug = settings.DEBUG
    if not debug:
        return Response(status_code=404, content="Not allowed")
    articles = [
        {'name': 'Багамы: как живёт страна, где почти нет налогов?',
         'description': 'Это место, где власти не взимают НДФЛ, закрывают '
                        'глаза на прирост капитала, не облагают налогом '
                        'наследство и освободили компании '
                        'от платежей на прибыль.',
         'category': 'экономика',
         'added_at': datetime.now()
         },
        {'name': 'Тонны метана в море: что случилось с '
                 'Северным Потоком после подрыва?',
         'description': 'После диверсии на газопроводе прошло почти 2 '
                        'года.',
         'category': 'события',
         'added_at': datetime.now()
         },
        {'name': 'Республика Самсунг: Как корпорации захватили Южную Корею?',
         'description': 'Южная Корея – высокоразвитая страна и пример '
                        'быстрого восстановления народного хозяйства '
                        'после тотальной разрухи.',
         'category': 'экономика',
         'added_at': datetime.now()
         },
    ]
    article_models = [ArticleModel(**article) for article in articles]
    for article_model in article_models:
        db.add(article_model)
        await db.commit()
        await db.refresh(article_model)
    return RedirectResponse("/blog/all/1", status_code=302)
