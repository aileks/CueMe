import os
import uuid

from flask import Flask, Response, redirect, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf

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
