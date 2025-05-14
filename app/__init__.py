import os
import uuid

import click
from flask import Flask, Response, redirect, request, send_from_directory
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf

from app.services.spotify_service import SpotifyService

from .config import Config
from .models import User, db
from .routes import auth_bp, playlist_bp

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(playlist_bp, url_prefix="/api/playlists")
app.config.from_object(Config)

login = LoginManager()
login.init_app(app)
login.login_view = "auth.unauthorized"  # type: ignore


@click.command("test-spotify")
@with_appcontext
def test_spotify_command():
    """Test the SpotifyService class functionality."""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Missing Spotify credentials in .env file")
        return

    service = SpotifyService(client_id=client_id, client_secret=client_secret)

    # Test getting genre list
    print("\n===== AVAILABLE GENRES =====")
    genres = service.get_genre_list()
    print(f"Found {len(genres)} genres")
    print(genres[:10])  # Print first 10 genres

    # Test finding tracks for a genre
    test_genre = "rock"
    print(f"\n===== TRACKS FOR GENRE: {test_genre} =====")
    tracks = service.find_tracks_by_genre(test_genre, limit=5)

    print(f"Found {len(tracks)} tracks")
    for i, track in enumerate(tracks[:5], 1):
        artist_names = ", ".join([artist["name"] for artist in track["artists"]])
        print(f"{i}. {track['name']} by {artist_names}")

    # Test getting audio features
    if tracks:
        print("\n===== AUDIO FEATURES =====")
        track_ids = [track["id"] for track in tracks[:2]]
        features = service.get_track_features(track_ids)

        for i, feature in enumerate(features, 1):
            print(f"\nTrack {i} features:")
            # Print a few key features
            for key in ["danceability", "energy", "tempo", "valence"]:
                if key in feature:
                    print(f"  {key}: {feature[key]}")


app.cli.add_command(test_spotify_command)


@login.user_loader
def load_user(user_id_str):
    try:
        user_uuid = uuid.UUID(user_id_str)
        return db.session.get(User, user_uuid)
    except ValueError:
        return None
    except Exception as e:
        app.logger.error(f"Error loading user {user_id_str}: {e}")
        return None


db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)

CORS(app)


@app.before_request
def https_redirect() -> Response | None:
    if os.environ.get("FLASK_ENV") == "prod":
        if request.headers.get("X-Forwarded-Proto") == "http":
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code)  # pyright: ignore


@app.after_request
def inject_csrf_token(response: Response) -> Response:
    response.set_cookie(
        "csrf_token",
        generate_csrf(),
        secure=True if os.environ.get("FLASK_ENV") == "production" else False,
        samesite="Strict" if os.environ.get("FLASK_ENV") == "production" else None,
        httponly=True,
    )
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def react_root(path) -> Response:
    if path == "favicon.ico":
        return send_from_directory("public", "favicon.ico")
    return app.send_static_file("index.html")


@app.errorhandler(404)
def not_found(e) -> Response:
    return app.send_static_file("index.html")
