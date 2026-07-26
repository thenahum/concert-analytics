import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True, repr=False)
class PostgresConfig:
    user: str | None
    password: str | None
    host: str | None
    port: int | None
    database: str | None


def get_postgres_config(load_env: bool = True, dotenv_path: str | Path | None = None) -> PostgresConfig:
    """Read Postgres configuration from the environment.

    `load_env=True` loads `.env` explicitly at call time. Importing this module
    never reads `.env`.
    """
    if load_env:
        load_dotenv(dotenv_path=dotenv_path)

    port = os.getenv("PGPORT")

    return PostgresConfig(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=int(port) if port else None,
        database=os.getenv("PGDATABASE"),
    )


def get_engine(config: PostgresConfig | None = None, load_env: bool = True):
    """Create a SQLAlchemy engine from Postgres configuration."""
    config = config or get_postgres_config(load_env=load_env)

    db_url = URL.create(
        "postgresql",
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )

    return create_engine(db_url)
