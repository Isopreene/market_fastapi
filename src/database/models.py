from datetime import datetime
from sqlalchemy import (Column, Integer, String,
                        DateTime, Computed, Index, Boolean)
from sqlalchemy_utils import EmailType
from .connection import Base
from sqlalchemy_utils.types.ts_vector import TSVectorType


class Article(Base):
    """Модель sqlalchemy для описания статьи"""
    __tablename__ = "articles"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    category: str = Column(String, index=True)
    description: str = Column(String)
    added_at: datetime = Column(DateTime)
    tsvector = (
        Column(TSVectorType("content",
                            regconfig="russian"),
               Computed("to_tsvector('russian', name || ' ' || description)",
                        persisted=True)))
    __table_args__ = (Index("idx_mymodel_content_tsv", tsvector,
                      postgresql_using="gin"),)

    def __repr__(self):
        return (f"name: {self.name}, "
                f"category: {self.category}, "
                f"description: {self.description}")


class User(Base):
    """Модель sqlalchemy для описания пользователя"""
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    email: str = Column(EmailType, unique=True)
    phone: str = Column(String)
    hashed_password: str = Column(String)
    added_at: datetime = Column(DateTime)
    activated: bool = Column(Boolean, default=False)

    def __repr__(self):
        return (f"email: {self.email}, name: {self.name}, password:"
                f" {self.hashed_password}")
