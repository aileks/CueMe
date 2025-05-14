import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    if SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://")

    SQLALCHEMY_ECHO = True

    # Spotify API Config
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
