from fastapi import FastAPI, Response, Request, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.models import Article as ArticleModel
from src.schemas.models import Article as ArticleSchema
from sqlalchemy.orm.exc import NoResultFound
from typing import List
from datetime import datetime
from sqlalchemy import func

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["Blog"])
router.mount("/static", StaticFiles(directory="templates"), name="templates")


@router.get("/all",
            response_class=HTMLResponse,
            response_model=ArticleSchema)
def list_all_articles(request:Request,
                      category:str="",
                      db: Session = Depends(get_db)):
    """Вернуть по GET-запросу список всех статей. Нужно добавить поиск по
    категориям и полнотекстовый"""
    categories = db.query(ArticleModel.category).distinct().all()
    categories = sorted([c[0] for c in categories])
    if category:
        articles = db.query(ArticleModel).filter_by(category=category).all()
    else:
        articles = db.query(ArticleModel).all()
    return templates.TemplateResponse("articles.html",
                                      {"request":request,
                                       "articles":articles,
                                       "categories": categories})

@router.post("/all",
             name="search_articles",
            response_class=HTMLResponse,
            response_model=ArticleSchema)
def search_articles(request:Request,
                    search_text:str="",
                    db: Session = Depends(get_db)):
    categories = db.query(ArticleModel.category).distinct().all()
    categories = sorted([c[0] for c in categories])
    if search_text:
        articles = db.query(ArticleModel).filter(ArticleModel.vector.match(
            search_text)).all()
    else:
        articles = db.query(ArticleModel).all()
    return templates.TemplateResponse("articles.html",
                                      {"request":request,
                                       "articles":articles,
                                       "categories": categories,
                                       "search_text": search_text})


@router.get("/{id_:int}",
            response_class=HTMLResponse,
            response_model=List[ArticleSchema])
def list_article(id_:int,
                 request: Request,
                 db: Session = Depends(get_db)):
    try:
        article = db.query(ArticleModel).filter_by(id=id_).one()
    except NoResultFound:
        return Response(f"Статья с id {id_} не найдена", status_code=404)
    return templates.TemplateResponse("article.html",
                                      {"request":request, "article":article})

@router.post("/create",
            response_model=ArticleSchema)
def post_article(model: ArticleSchema,
                 db: Session = Depends(get_db)):
    article = ArticleModel(name=model.name,
                           category=model.category,
                           description=model.description,
                           added_at=datetime.now())
    db.add(article)
    db.commit()
    db.refresh(article)
    return RedirectResponse(f"{article.id}", status_code=301)

@router.post("/create_start",
            response_model=ArticleSchema)
def post_start_articles(request: Request,
                        db: Session = Depends(get_db)):
    articles = [
        {'name': 'Багамы: как живёт страна, где почти нет налогов?',
         'description': 'Это место, где власти не взимают НДФЛ, закрывают '
                        'глаза на прирост капитала, не облагают налогом наследство и освободили компании от платежей на прибыль.',
         'category': 'экономика',
         'added_at': datetime.now()
         },
        {'name': 'Тонны метана в море: что случилось с Северным Потоком после подрыва?',
         'description': 'После диверсии на газопроводе прошло почти 2 '
                        'года.',
         'category': 'события',
         'added_at': datetime.now()
         },
        {'name': 'Республика Самсунг: Как корпорации захватили Южную Корею?',
         'description': 'Южная Корея – высокоразвитая страна и пример '
                        'быстрого восстановления народного хозяйства после тотальной разрухи.',
         'category': 'экономика',
         'added_at': datetime.now()
         },
    ]
    article_models = [ArticleModel(**article) for article in articles]
    for article_model in article_models:
        db.add(article_model)
        db.commit()
        db.refresh(article_model)
    categories = db.query(ArticleModel.category).distinct().all()
    categories = sorted([c[0] for c in categories])
    return templates.TemplateResponse("articles.html",
                                      {"request":request,
                                       "articles":articles,
                                       "categories": categories})