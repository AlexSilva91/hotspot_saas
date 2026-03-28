from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.user_controller.user_controller import UserController  

user_bp = Blueprint("users", __name__)

@user_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    data = UserController.list()
    return render_template("users/list.html", **data)

@user_bp.route("/users/create", methods=["POST"])
@login_required
def create_user():
    return UserController.create()

@user_bp.route("/users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):
    return UserController.update(user_id)

@user_bp.route("/users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    return UserController.delete(user_id)