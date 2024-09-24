import sqlalchemy
from sqlalchemy_utils import create_database, database_exists

def create_database_with_schema_if_not_exists(connection, schemas):
    for schema in schemas:
        if not connection.dialect.has_schema(connection, schema):
            connection.execute(sqlalchemy.schema.CreateSchema(schema))