from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from flask_login import login_required
from werkzeug.security import generate_password_hash
from app.services.user_service import UserService
from app.services.tenant_service import TenantService

user_bp = Blueprint("users", __name__)

# LISTAR
@user_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    users = UserService.list_users()
    tenants = TenantService.list_tenants()

    form_data = session.pop("form_data", {})
    form_errors = session.pop("form_errors", {})

    return render_template(
        "users/list.html",
        users=users,
        tenants=tenants,
        form_data=form_data,
        form_errors=form_errors
    )

# CRIAR
@user_bp.route("/users/create", methods=["POST"])
@login_required
def create_user():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "").strip()
    tenant_id = request.form.get("tenant_id") or None
    active = request.form.get("active", "true") == "true"

    errors = {}
    if not email: errors["email"] = "E-mail é obrigatório"
    if not password: errors["password"] = "Senha é obrigatória"
    if not role: errors["role"] = "Função é obrigatória"

    if errors:
        session["form_data"] = {"email": email, "role": role, "tenant_id": tenant_id}
        session["form_errors"] = errors
        flash("Por favor, corrija os erros no formulário", "error")
        return redirect(url_for("users.list_users"))

    data = {
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": role,
        "tenant_id": tenant_id,
        "active": active
    }

    result = UserService.create_user(data)

    if result["success"]:
        flash("Usuário criado com sucesso!", "success")
    else:
        session["form_data"] = {"email": email, "role": role, "tenant_id": tenant_id}
        session["form_errors"] = result.get("errors", {})
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("users.list_users"))

# ATUALIZAR
@user_bp.route("/users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "").strip()
    tenant_id = request.form.get("tenant_id") or None
    active = request.form.get("active", "true") == "true"

    errors = {}
    if not email: errors["email"] = "E-mail é obrigatório"
    if not role: errors["role"] = "Função é obrigatória"

    if errors:
        for msg in errors.values():
            flash(msg, "error")
        return redirect(url_for("users.list_users"))

    data = {"email": email, "role": role, "tenant_id": tenant_id, "active": active}
    if password: data["password_hash"] = generate_password_hash(password)

    result = UserService.update_user(user_id, data)

    if result["success"]:
        flash("Usuário atualizado com sucesso!", "success")
    else:
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("users.list_users"))

# DELETAR
@user_bp.route("/users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    result = UserService.delete_user(user_id)

    if result.get("success", False):
        flash("Usuário excluído com sucesso!", "success")
    else:
        for msg in result.get("errors", {}).values():
            flash(msg, "error")

    return redirect(url_for("users.list_users"))