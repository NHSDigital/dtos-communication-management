from alembic import context
import alembic_postgresql_enum
import dotenv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

import migrations.migrator as migrator


# Load environment variables
dotenv.load_dotenv(dotenv_path=os.getenv("ENV_FILE", ".env.local"))

migrator.migrate_database(offline=context.is_offline_mode())
