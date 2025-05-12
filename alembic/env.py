import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ⬇️ Подгружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

# Подключение логирования из alembic.ini
config = context.config
fileConfig(config.config_file_name)

# Заменяем sqlalchemy.url из alembic.ini на переменную окружения
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Импортируем модели
from bot.database.models import Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Миграции в офлайн-режиме (без подключения к БД)."""
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
    """Миграции в онлайн-режиме (с подключением к БД)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
