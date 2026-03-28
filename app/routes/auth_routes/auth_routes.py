from flask import Blueprint, render_template
from app.controller.auth_controller.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    data = AuthController.login()
    if isinstance(data, dict):
        return render_template("auth/login.html", **data)
    return data

@auth_bp.route("/logout")
def logout():
    return AuthController.logout()