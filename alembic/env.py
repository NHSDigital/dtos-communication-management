import os
from logging.config import fileConfig
import logging
import dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy_utils import database_exists, create_database
from alembic import context
from database.models import Base
import alembic_postgresql_enum

# Load environment variables
dotenv.load_dotenv(dotenv_path=os.getenv("ENV_FILE", ".env.local"))


def connection_string() -> str:
    return (
        f"postgresql+psycopg2://{os.environ['DATABASE_USER']}"
        f":{os.environ['DATABASE_PASSWORD']}"
        f"@{os.environ['DATABASE_HOST']}"
        f"/{os.environ['DATABASE_NAME']}"
        f"?sslmode={os.environ.get('DATABASE_SSLMODE', 'require')}"
    )


def run_migrations_offline(connection_string: str):
    context.configure(
        url=connection_string,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(connection_string: str):
    connectable = create_engine(
        connection_string,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=Base.metadata
        )
        with context.begin_transaction():
            context.run_migrations()


def create_database_if_not_exists(connection_string: str) -> None:
    logger = logging.getLogger("alembic")
    try:
        if not database_exists(connection_string):
            create_database(connection_string)
            logger.info(f"Database '{os.environ['DATABASE_NAME']}' created successfully.")
    except Exception as e:
        logger.error(f"Error checking or creating database: {e}")


def configure_alembic(connection_string: str) -> None:
    context.config.set_main_option("sqlalchemy.url", connection_string)

    if context.config.config_file_name is not None:
        fileConfig(context.config.config_file_name)


# Perform steps to run migrations
connection_string: str = connection_string()
configure_alembic(connection_string)
create_database_if_not_exists(connection_string)

if context.is_offline_mode():
    run_migrations_offline(connection_string)
else:
    run_migrations_online(connection_string)
