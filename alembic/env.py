from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
# Добавление пути  в sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models.feature import Feature
from app.core.config import DATABASE_URL

config = context.config
fileConfig(config.config_file_name)

# Переопределение sqlalchemy.url из alembic.ini значением из конфига
config.set_main_option("sqlalchemy.url", str(DATABASE_URL))

target_metadata = Base.metadata 

def run_migrations_offline():
    context.configure(url=str(DATABASE_URL), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": str(DATABASE_URL)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()