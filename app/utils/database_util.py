from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed

from app.infrastructure.logging_config import configure_logging
from app.infrastructure.settings import settings
from app.utils.logging_util import LogLevel, log_message
from alembic.config import Config

def run_migrations():
    try:
        log_message(LogLevel.INFO, "Database migrations starting")

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # reset logging configuration
        configure_logging()

        log_message(LogLevel.INFO, "Database migrations completed successfully")

    except Exception as e:
        log_message(LogLevel.ERROR, "Database migration failed", error=str(e))
        raise


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def create_db_engine():
    return create_engine(
        url=settings.POSTGRES_URL,
        pool_pre_ping=True,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DBBase = declarative_base()


