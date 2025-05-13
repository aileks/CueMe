import uuid

from .db import SCHEMA, UUIDColumnType, db, environment


class Track(db.Model):
    __tablename__ = "tracks"

    if environment == "prod":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(UUIDColumnType, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))

    playlists = db.relationship("PlaylistTrack", back_populates="track")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
        }
