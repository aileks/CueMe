import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Uuid as GenericUUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

environment = os.getenv("FLASK_ENV")
SCHEMA = os.environ.get("SCHEMA")


db = SQLAlchemy()

# Determine the UUID column type based on the DBMS
db_uri = os.environ.get("DATABASE_URL", "")
if db_uri.startswith("postgresql"):
    UUIDColumnType = PG_UUID(as_uuid=True)
else:
    UUIDColumnType = GenericUUID(as_uuid=True)


def add_prefix_for_prod(attr):
    if environment == "prod":
        return f"{SCHEMA}.{attr}"
    else:
        return attr
