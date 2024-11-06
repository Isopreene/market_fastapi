from datetime import datetime
from httpx import AsyncClient, QueryParams
from pydantic import ValidationError
from src.database.models import Article as ArticleModel
from src.schemas.blog import Article
from tests.conftest import async_session_maker
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
import pytest


@pytest.mark.asyncio
async def test_all_articles(async_client: AsyncClient):
    response = await async_client.get("/blog/all")
    assert response.status_code == 302
    assert response.headers["Location"] == "/blog/all/1"


@pytest.mark.asyncio
async def test_all_articles_with_pages(async_client: AsyncClient):
    response = await async_client.get("/blog/all/1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_all_articles_with_pages_add(async_client: AsyncClient):
    response = await async_client.get("/blog/all/1")
    assert response.status_code == 200
    # дописать


@pytest.mark.asyncio
async def test_create_right(async_client: AsyncClient, test_right_article,
                            ):
    schema = test_right_article
    async with async_session_maker() as session:
        articles = await session.execute(select(ArticleModel))
        articles = articles.scalars().all()
        l_art = len(articles)

        article = ArticleModel(name=schema.name,
                               category=schema.category,
                               description=schema.description,
                               added_at=datetime.now())
        response = await async_client.post("/blog/create",
                                           json=jsonable_encoder(article))

        assert response.status_code == 302
        articles = await session.execute(select(ArticleModel))
        articles = articles.scalars().all()
        l_new = len(articles)
        assert l_new == l_art + 1
        assert response.headers["Location"] == f"{l_new}"


@pytest.mark.asyncio
async def test_create_wrong(async_client: AsyncClient):
    with pytest.raises(ValidationError):
        Article(name=21321412,
                category=False,
                description=None)


@pytest.mark.asyncio
async def test_search(async_client: AsyncClient, test_right_article,
                      add_right_article
                      ) -> None:
    schema = test_right_article
    article = ArticleModel(name=schema.name,
                           category=schema.category,
                           description=schema.description,
                           added_at=datetime.now())
    async with async_session_maker() as session:
        session.add(article)
        await session.commit()
        await session.refresh(article)
        q = QueryParams({"search_text": test_right_article.description[
                                           :10]})
        response = await async_client.post("/blog/all?search_text",
                                           params=q)
        assert response.status_code == 200
        print(response.content.decode('utf-8'))
    # дописать


@pytest.mark.asyncio
async def test_one_article(async_client: AsyncClient):
    response = await async_client.get("/blog/1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_start(async_client: AsyncClient):
    async with async_session_maker() as session:
        articles = await session.execute(select(ArticleModel))
        articles = articles.scalars().all()
        l_art = len(articles)
        response = await async_client.post("/blog/create_start")
        articles = await session.execute(select(ArticleModel))
        articles = articles.scalars().all()
        assert len(articles) == l_art + 3
        assert response.status_code == 302
