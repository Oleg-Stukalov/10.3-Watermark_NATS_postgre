import asyncio
from logging.config import fileConfig

from alembic import context
from dynaconf import Dynaconf
from sqlalchemy.ext.asyncio import create_async_engine

from config import Config
from database.models import Base


config = context.config

# Setup logging from alembic.ini config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def include_name(name, type_, _):
    if type_ == 'table':
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    settings = Dynaconf(
        envvar_prefix='APP_CONF',
        settings_files=[
            'settings.toml',
            '.secrets.toml',
        ],
    )
    # Convert Dynaconf LazySettings to nested dict for Pydantic validation
    app_config: Config = Config.model_validate(settings.as_dict())

    context.configure(
        url=app_config.db.uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    settings = Dynaconf(
        envvar_prefix='APP_CONF',
        settings_files=[
            'settings.toml',
            '.secrets.toml',
        ],
    )
    app_config: Config = Config.model_validate(settings.as_dict())

    connectable = create_async_engine(
        app_config.db.uri,
        **app_config.db.orm.engine.dict()
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
