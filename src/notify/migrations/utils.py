from alembic import command
from alembic.config import Config
import io
import os


def alembic_migrate() -> str | None:
    script_location = os.path.join(os.path.dirname(__file__))
    output_buffer = io.StringIO()
    alembic_cfg = Config(stdout=output_buffer)
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', connection_string())
    command.upgrade(alembic_cfg, 'head')
    command.current(alembic_cfg, verbose=True)
    return output_buffer.getvalue()


def connection_string() -> str:
    return (
        f"postgresql+psycopg2://{os.environ['DATABASE_USER']}"
        f":{os.environ['DATABASE_PASSWORD']}"
        f"@{os.environ['DATABASE_HOST']}"
        f"/{os.environ['DATABASE_NAME']}"
        f"?sslmode={os.environ.get('DATABASE_SSLMODE', 'require')}"
    )
