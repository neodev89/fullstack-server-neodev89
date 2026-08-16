# sessionDb = "postgresql+psycopg://postgres:n5R13zRsiZiGs7T3@db.nievkcazlxioutxagdpc.supabase.co:5432/postgres"
# sessionDb1 = "postgresql+psycopg://postgres.nievkcazlxioutxagdpc:n5R13zRsiZiGs7T3@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
sessionDb2 = "postgresql+psycopg://postgres.nievkcazlxioutxagdpc:n5R13zRsiZiGs7T3@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"
# directUrl = "postgresql+psycopg://postgres:[n5R13zRsiZiGs7T3]@db.nievkcazlxioutxagdpc.supabase.co:5432/postgres"

# db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    sessionDb2,
    echo=True,
    # ⬇️ AGGIUNGI QUESTO BLOCCO PER IL POOLER DI SUPABASE ⬇️
    connect_args={
        "autocommit": True
    }
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
