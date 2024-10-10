from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Computed, Index
from .connection import Base
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator
from sqlalchemy_utils.types.ts_vector import TSVectorType


class Article(Base):
    """Модель sqlalchemy для описания статьи"""
    __tablename__ = "articles"
    id:int = Column(Integer, primary_key=True, index=True)
    name:str = Column(String)
    category:str = Column(String, index=True)
    description:str = Column(String)
    added_at:datetime = Column(DateTime)
    # vector = (
    #     Column( TSVectorType("content", regconfig="english"), Computed(
    #     "to_tsvector('english', name || ' ' || description)",
    #     persisted=True)))
    # __table_args__ = (Index("idx_mymodel_content_tsv", vector,
    #              postgresql_using="gin"),)

    def __repr__(self):
        return f"name: {self.name}, category: {self.category}, description: {self.description}"
