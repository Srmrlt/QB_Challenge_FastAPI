from typing import Annotated
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.database.config import settings


engine = create_async_engine(
    url=settings.db_url_asyncpg,
    echo=True,
)

session_factory = async_sessionmaker(engine, expire_on_commit=False)

# Create a custom type annotation for string fields limited to 256 characters.
str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    """
    Define a base class for all SQLAlchemy Declarative models.
    It provides a common __repr__ method and a mapping from type annotations to SQLAlchemy types.
    """
    type_annotation_map = {
        str_256: String(256)
    }

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
