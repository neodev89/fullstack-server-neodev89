sessionDb = "postgresql+asyncpg://postgres.nievkcazlxioutxagdpc:[EserciziEProgettiNext89]@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"
directUrl = "postgresql+asyncpg://postgres:[EserciziEProgettiNext89]@db.nievkcazlxioutxagdpc.supabase.co:5432/postgres"

# db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    directUrl,
    echo=True,
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
