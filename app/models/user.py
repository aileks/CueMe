import uuid

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db import SCHEMA, UUIDColumnType, db, environment


class User(db.Model, UserMixin):
    __tablename__ = "users"

    if environment == "prod":
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
