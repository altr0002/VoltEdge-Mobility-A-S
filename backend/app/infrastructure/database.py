from collections.abc import Generator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg2://voltedge:voltedge@postgres:5432/"
        "voltedge_monitoring"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class Base(DeclarativeBase):
    pass


settings = Settings()


def create_database_engine(database_url: str):
    engine_options = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        if database_url.endswith(":memory:"):
            engine_options["poolclass"] = StaticPool

    return create_engine(database_url, **engine_options)


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
