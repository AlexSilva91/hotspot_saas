from flask import Blueprint, request, render_template, redirect, url_for
from app.services.user_service import UserService
from app.services.tenant_service import TenantService

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["GET"])
def list_users():

    users = UserService.list_users()
    tenants = TenantService.list_tenants()

    return render_template(
        "users/list.html",
        users=users,
        tenants=tenants
    )

@user_bp.route("/users/create", methods=["POST"])
def create_user():

    data = {
        "email": request.form.get("email"),
        "password_hash": request.form.get("password"),
        "role": request.form.get("role"),
        "tenant_id": request.form.get("tenant_id")
    }

    UserService.create_user(data)

    return redirect(url_for("users.list_users"))


@user_bp.route("/users/<uuid:user_id>/edit", methods=["GET"])
def edit_user_page(user_id):

    user = UserService.get_user(user_id)
    tenants = TenantService.list_tenants()
    return render_template(
        "users/edit.html",
        user=user,
        tenants=tenants
    )


@user_bp.route("/users/<uuid:user_id>/edit", methods=["POST"])
def update_user(user_id):

    data = {
        "email": request.form.get("email"),
        "role": request.form.get("role"),
        "tenant_id": request.form.get("tenant_id")
    }

    UserService.update_user(user_id, data)

    return redirect(url_for("users.list_users"))


@user_bp.route("/users/<uuid:user_id>/delete", methods=["POST"])
def delete_user(user_id):

    UserService.delete_user(user_id)

    return redirect(url_for("users.list_users"))