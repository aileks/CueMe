import os

from flask import Flask, redirect, request
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .models import db

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
app.config.from_object(Config)
Migrate(app, db)
CORS(app)


@app.before_request
def https_redirect():
    if os.environ.get("FLASK_ENV") == "production":
        if request.headers.get("X-Forwarded-Proto") == "http":
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def react_root(path):
    if path == "favicon.ico":
        return app.send_from_directory("public", "favicon.ico")  # pyright: ignore
    return app.send_static_file("index.html")


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")
