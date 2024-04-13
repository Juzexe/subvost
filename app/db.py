from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(settings.db_url)

Base = declarative_base()

AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)
