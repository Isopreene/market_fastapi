from datetime import datetime
from src.schemas.blog import Article
import pytest
from src.database.models import Article as ArticleModel, User as UserModel
from src.app.routes.mail import mail_cache
from src.app.back.mail_back import MailCache
from src.app.back.users_back import get_password_hash
from tests.conftest import async_session_maker


@pytest.fixture
def test_right_article():
    return Article(name="Это тестовая статья",
                   category="Это тестовая категория",
                   description="Это описание тестовой статьи",)


@pytest.fixture
async def add_right_article(test_right_article):
    async with async_session_maker() as session:
        schema = test_right_article
        article = ArticleModel(name=schema.name,
                               category=schema.category,
                               description=schema.description,
                               added_at=datetime.now())
        session.add(article)
        await session.commit()
        await session.refresh(article)
    return article


@pytest.fixture
def user_right_register_data():
    return {
        "name": "John Doe",
        "email": "johndoe@gmail.com",
        "password": "verystrongpassword123",
        "repeat_password": "verystrongpassword123",
        "phone": "+79001234567"
           }


@pytest.fixture
def user_wrong_register_data():
    return {
        "name": None,
        "email": 214125665432,
        "password": "verystrongpassword123",
        "repeat_password": "verystrongpassword21424124124123",
        "phone": False
    }


@pytest.fixture
def user_right_login_data():
    return {
         "email": "johndoe@gmail.com",
         "password": "verystrongpassword123",
         }


@pytest.fixture
def user_wrong_login_data():
    return {
         "email": 214125665432,
         "password": "verystrongpassword123"}


@pytest.fixture
def user_right_recovery_data():
    return {
         "email": "johndoe@gmail.com"
         }


@pytest.fixture
def user_wrong_recovery_data():
    return {
         "email": 214125665432}


@pytest.fixture
async def generate_mail_link(cache: MailCache = mail_cache):
    link = cache.generate_link("johndoe@gmail.com", route="activate_link")
    return link


@pytest.fixture
async def register_user(async_session, user_right_register_data):
    schema = user_right_register_data
    user = UserModel(name=schema["name"],
                     email=schema["email"],
                     hashed_password=get_password_hash(schema['password']),
                     added_at=datetime.now())
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user
