import uuid

from sqlalchemy import ForeignKey

from .db import SCHEMA, UUIDColumnType, add_prefix_for_prod, db, environment


class Playlist(db.Model):
    __tablename__ = "playlists"

    if environment == "prod":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(UUIDColumnType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        UUIDColumnType, ForeignKey(add_prefix_for_prod("users.id")), nullable=False
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="playlists")
    tracks = db.relationship(
        "PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "track_count": len(self.tracks),  # type: ignore
        }

    def to_dict_with_tracks(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "tracks": [track.to_dict() for track in self.tracks],  # type: ignore
        }
