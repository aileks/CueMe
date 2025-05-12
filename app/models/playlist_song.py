import uuid

from sqlalchemy import ForeignKey

from .db import SCHEMA, UUIDColumnType, add_prefix_for_prod, db, environment


class PlaylistSong(db.Model):
    __tablename__ = "playlist_songs"

    if environment == "prod":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(UUIDColumnType, primary_key=True, default=uuid.uuid4)
    playlist_id = db.Column(
        UUIDColumnType, ForeignKey(add_prefix_for_prod("playlists.id")), nullable=False
    )
    song_id = db.Column(
        UUIDColumnType, ForeignKey(add_prefix_for_prod("songs.id")), nullable=False
    )
    position = db.Column(db.Integer, nullable=False)

    # Relationships
    playlist = db.relationship("Playlist", back_populates="songs")
    song = db.relationship("Song", back_populates="playlists")

    def to_dict(self):
        return {
            "id": self.id,
            "playlist_id": self.playlist_id,
            "song_id": self.song_id,
            "position": self.position,
            "song": self.song.to_dict(),
        }
