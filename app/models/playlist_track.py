import uuid

from sqlalchemy import ForeignKey

from .db import SCHEMA, UUIDColumnType, add_prefix_for_prod, db, environment


class PlaylistTrack(db.Model):
    __tablename__ = "playlist_tracks"

    if environment == "prod":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(UUIDColumnType, primary_key=True, default=uuid.uuid4)
    playlist_id = db.Column(
        UUIDColumnType, ForeignKey(add_prefix_for_prod("playlists.id")), nullable=False
    )
    track_id = db.Column(
        UUIDColumnType, ForeignKey(add_prefix_for_prod("tracks.id")), nullable=False
    )
    position = db.Column(db.Integer, nullable=False)

    # Relationships
    playlist = db.relationship("Playlist", back_populates="tracks")
    track = db.relationship("track", back_populates="playlists")

    def to_dict(self):
        return {
            "id": self.id,
            "playlist_id": self.playlist_id,
            "track_id": self.track_id,
            "position": self.position,
            "track": self.track.to_dict(),
        }
