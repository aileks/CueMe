import os

from flask import Flask, redirect, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate

# from flask_login import LoginManager
from .config import Config
from .models import db

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
app.config.from_object(Config)

# login = LoginManager(app)
# login.login_view = "auth.unauthorized"


# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))


db.init_app(app)
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
        return send_from_directory("public", "favicon.ico")
    return app.send_static_file("index.html")


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")
