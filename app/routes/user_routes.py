from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_required
from werkzeug.security import generate_password_hash
from app.controller.base_controller import BaseController
from app.services.user_service import UserService
from app.services.tenant_service import TenantService


user_bp = Blueprint("users", __name__)


# LISTAR
@user_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    result = UserService.list()
    users = result.get("data", [])
    
    tenants_result = TenantService.list()
    tenants = tenants_result.get("data", [])

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
    if not email:
        errors["email"] = "E-mail é obrigatório"
    if not password:
        errors["password"] = "Senha é obrigatória"
    if not role:
        errors["role"] = "Função é obrigatória"

    if errors:
        session["form_data"] = {"email": email, "role": role, "tenant_id": tenant_id, "active": active}
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

    result = UserService.create(data)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário criado com sucesso!",
        error_default="Erro ao criar usuário",
        redirect_to="users.list_users",
        form_data={"email": email, "role": role, "tenant_id": tenant_id, "active": active}
    )


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
    if not email:
        errors["email"] = "E-mail é obrigatório"
    if not role:
        errors["role"] = "Função é obrigatória"

    if errors:
        for msg in errors.values():
            flash(msg, "error")
        return redirect(url_for("users.list_users"))

    data = {
        "email": email, 
        "role": role, 
        "tenant_id": tenant_id, 
        "active": active
    }
    
    if password:
        data["password_hash"] = generate_password_hash(password)

    result = UserService.update(user_id, data)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário atualizado com sucesso!",
        error_default="Erro ao atualizar usuário",
        redirect_to="users.list_users"
    )


# DELETAR
@user_bp.route("/users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    result = UserService.delete(user_id)

    return BaseController.handle_result(
        result=result,
        success_message="Usuário excluído com sucesso!",
        error_default="Erro ao excluir usuário",
        redirect_to="users.list_users"
    )