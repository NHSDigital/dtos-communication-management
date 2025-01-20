import os
from logging.config import fileConfig
import logging
import dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy_utils import database_exists, create_database
from alembic import context
from database.models import Base

# Load environment variables
dotenv.load_dotenv(dotenv_path=os.getenv("ENV_FILE", ".env.local"))

# Get logger
logger = logging.getLogger("alembic")

# Construct the DB connection string
DATABASE_NAME = os.environ["DATABASE_NAME"]
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_SSLMODE = os.getenv("DATABASE_SSLMODE", "require")

connection_string = (
    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    f"?sslmode={DATABASE_SSLMODE}"
)

# Check and create the database if it doesn't exist
try:
    engine = create_engine(connection_string.rsplit("/", 1)[0])  # Remove DB name
    if not database_exists(connection_string):
        create_database(connection_string)
        logger.info(f"Database '{DATABASE_NAME}' created successfully.")
except Exception as e:
    logger.error(f"Error checking or creating database: {e}")

# Pass the connection string to Alembic
config = context.config
config.set_main_option("sqlalchemy.url", connection_string)

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        connection_string,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
