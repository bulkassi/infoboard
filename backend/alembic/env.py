from __future__ import annotations

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

from sqlmodel import SQLModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        # ignore logging config issues when alembic.ini lacks expected sections
        pass

# Import application metadata and engine
try:
    from app.core.db import engine  # use app's configured engine
except Exception:  # pragma: no cover - import-time issues
    # if the app package isn't importable, add the project 'backend' dir to sys.path
    backend_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_path))
    from app.core.db import engine

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    raise NotImplementedError("Offline mode is not supported for this env.py")


def run_migrations_online() -> None:
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
