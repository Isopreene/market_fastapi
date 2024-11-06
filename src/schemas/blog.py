from pydantic import BaseModel


class Article(BaseModel):
    """Модель pydantic для описания статьи"""
    name: str
    category: str
    description: str
