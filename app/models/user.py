import os
import uuid

from flask_login import UserMixin
from sqlalchemy import Uuid as GenericUUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from werkzeug.security import check_password_hash, generate_password_hash

from .db import SCHEMA, db, environment

db_uri = os.environ.get("DATABASE_URL", "")

if db_uri.startswith("postgresql"):
    UUIDColumnType = PG_UUID(as_uuid=True)
else:
    UUIDColumnType = GenericUUID(as_uuid=True)


class User(UserMixin):
    __tablename__ = "users"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(UUIDColumnType, primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)

    @property
    def password(self) -> str:
        return self.hashed_password

    @password.setter
    def password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username, "email": self.email}
