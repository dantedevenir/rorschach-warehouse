from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData, create_engine, text, inspect
from sqlalchemy_utils import database_exists, create_database
from alembic import config as alembic_config
import os
import toml

Base = declarative_base()

config = alembic_config.Config("alembic.ini")
ENV_PATH = os.getenv('ENV_PATH')
file_path = os.path.join(f'{ENV_PATH}/database.toml')
env_config = toml.load(file_path)

database = env_config["database"][0]

user = database["user"]
password = database["password"]
host = database["host"]
port = database["port"]
type = database["type"]
conn = database["conn"]
database_name = database["database"]

section = config.get_section(config.config_ini_section)
if section:
    db_url = section["sqlalchemy.url"].format(
        type, conn, user, password, host, port, database_name
    )

if not database_exists(db_url):
    create_database(db_url)

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)

if inspect(engine).has_schema("providers"):
    with Session() as session:
        if inspect(engine).has_table("name", schema="providers"):
            session.execute(text("SELECT providers.insert_name_data();"))
        if inspect(engine).has_table("type", schema="providers"):
            session.execute(text("SELECT providers.insert_type_data();"))
        if inspect(engine).has_table("source_type", schema="providers"):
            session.execute(text("SELECT providers.insert_source_type_data();"))
        session.commit()

if inspect(engine).has_schema("policies"):
    with Session() as session:
        if inspect(engine).has_table("status", schema="policies"):
            session.execute(text("SELECT policies.insert_status_data();"))
        if inspect(engine).has_table("member_type", schema="policies"):
            session.execute(text("SELECT policies.insert_member_type_data();"))
        session.commit()