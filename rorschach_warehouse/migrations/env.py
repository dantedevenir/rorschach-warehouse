from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import re
from db.base import Base
from models import policies as pl
from models import snapshots as ss
from models import providers as pr
import os
import toml
from alembic import config as alembic_config
from models.enum import enumModel

import alembic_postgresql_enum as alembic_postgresql_enum

from alembic_utils.pg_function import PGFunction
from alembic_utils.replaceable_entity import register_entities
from migrations.initial import create_database_with_schema_if_not_exists

def create_insert_function(enum, schema):
    values_str = ", ".join(f"('{name}')" for name in enum.__members__.keys()).replace('"', "'")
    enum_name = enum.__name__
    new_name = re.sub(r'(?<!^)(?=[A-Z])', '_', enum_name).lower()
    return PGFunction(
        schema=schema,
        signature=f'insert_{new_name}_data()',
        definition=f"""
        RETURNS void AS
        $$
        BEGIN
            INSERT INTO {schema}.{new_name} (name) VALUES
                {values_str}
            ON CONFLICT (name)
            DO NOTHING;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

# Registra la función
functions = []
for enum, schema in enumModel.items():
    print("Enum: ", enum, "Schema:", schema)
    functions.append(create_insert_function(enum, schema))
register_entities(functions)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.


config = alembic_config.Config("alembic.ini")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = Base.metadata

# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# db.. etc.

ENV_PATH = os.getenv('ENV_PATH')
file_path = os.path.join(f'{ENV_PATH}/database.toml')
env_config = toml.load(file_path)

DB_USER = env_config["database"][0]["user"]
DB_PASS = env_config["database"][0]["password"]
DB_HOST = env_config["database"][0]["host"]
DB_PORT = env_config["database"][0]["port"]
DB_TYPE = env_config["database"][0]["type"]
DB_CONN = env_config["database"][0]["conn"]
DB_NAME = env_config["database"][0]["database"]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    if(section := config.get_section(config.config_ini_section)):
        url = section["sqlalchemy.url"].format(
            DB_TYPE, DB_CONN, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
        )
    
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            include_schemas=True,
            version_table_schema="inpotras",
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    if(section := config.get_section(config.config_ini_section)):
        url = section["sqlalchemy.url"].format(
            DB_TYPE, DB_CONN, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
        )
        section["sqlalchemy.url"] = url
        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            create_database_with_schema_if_not_exists(connection, ['policies', 'providers', 'snapshots'])
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
