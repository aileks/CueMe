from flask import Blueprint, request
from flask_login import current_user, login_user
from flask_login.utils import logout_user

from app import db
from app.forms import RegistrationForm
from app.forms.login_form import LoginForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def authenticate() -> dict | tuple[dict, int]:
    if current_user.is_authenticated:
        return current_user.to_dict()

    return {"errors": {"message": "Unauthorized"}}, 401


@auth_bp.route("/register", methods=["POST"])
def register() -> dict | tuple[dict, int]:
    form = RegistrationForm()
    form["csrf_token"].data = request.cookies["csrf_token"]

    if form.validate_on_submit():
        user = User(
            username=form.data["username"],  # type: ignore
            email=form.data["email"],  # type: ignore
            password=form.data["password"],  # type: ignore
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return user.to_dict()

    return form.errors, 401


@auth_bp.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    form["csrf_token"].data = request.cookies["csrf_token"]

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.data["email"]).first()
        if user and user.check_password(form.data["password"]):
            login_user(user)
            return user.to_dict()

        return {"errors": {"message": "Invalid email or password"}}, 401

    return form.errors, 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return {"message": "Logged out successfully"}


@auth_bp.route("/unauthorized")
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {"errors": {"message": "Unauthorized"}}, 401
