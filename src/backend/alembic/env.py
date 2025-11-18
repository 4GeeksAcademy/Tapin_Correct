from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add parent directory to path to allow backend imports
alembic_dir = os.path.dirname(__file__)
backend_dir = os.path.abspath(os.path.join(alembic_dir, ".."))
src_dir = os.path.abspath(os.path.join(backend_dir, ".."))
sys.path.insert(0, src_dir)
sys.path.insert(0, backend_dir)

# Import the app and db to get the metadata for autogenerate
import backend.app as app_module

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

target_metadata = app_module.db.metadata

# Allow overriding the sqlalchemy URL using the environment variable. This lets
# CI or local envs set SQLALCHEMY_DATABASE_URI without editing alembic.ini
env_db_url = os.environ.get("SQLALCHEMY_DATABASE_URI")
if env_db_url:
    config.set_main_option("sqlalchemy.url", env_db_url)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
