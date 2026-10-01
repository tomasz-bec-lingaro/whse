from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def create_database_engine(database_url: str) -> Engine:
    engine_options = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        if ":memory:" in database_url:
            engine_options["poolclass"] = StaticPool
    return create_engine(database_url, **engine_options)


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
