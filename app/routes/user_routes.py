from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app.services.user_service import UserService
from app.services.tenant_service import TenantService
from app.decorators.login_required import login_required

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    users = UserService.list_users()
    tenants = TenantService.list_tenants()
    
    # Recupera dados do formulário da sessão se existirem (para caso de erro)
    form_data = session.pop('form_data', {})
    form_errors = session.pop('form_errors', {})

    return render_template(
        "users/list.html",
        users=users,
        tenants=tenants,
        form_data=form_data,
        form_errors=form_errors
    )


@user_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    if request.method == "GET":
        # Exibe o formulário
        tenants = TenantService.list_tenants()
        
        # Recupera dados do formulário da sessão se existirem (para caso de erro)
        form_data = session.pop('form_data', {})
        form_errors = session.pop('form_errors', {})
        
        return render_template(
            "users/create.html",  
            tenants=tenants,
            form_data=form_data,
            form_errors=form_errors
        )
    
    elif request.method == "POST":
        # Processa o formulário
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip()
        tenant_id = request.form.get("tenant_id", "").strip()
        
        # Se tenant_id for vazio, converte para None
        if tenant_id == "":
            tenant_id = None
        
        # Validação rápida no route também
        errors = {}
        if not email:
            errors['email'] = "E-mail é obrigatório"
        if not password:
            errors['password'] = "Senha é obrigatória"
        if not role:
            errors['role'] = "Função é obrigatória"
        
        if errors:
            # Salva os dados e erros na sessão
            session['form_data'] = {
                'email': email,
                'role': role,
                'tenant_id': tenant_id
            }
            session['form_errors'] = errors
            flash("Por favor, corrija os erros no formulário", "error")
            return redirect(url_for("users.create_user"))
        
        # Gera hash da senha
        hashed_password = generate_password_hash(password)

        data = {
            "email": email,
            "password_hash": hashed_password,
            "role": role,
            "tenant_id": tenant_id
        }

        # Chama o service que faz a validação completa
        result = UserService.create_user(data)

        if result['success']:
            flash("Usuário criado com sucesso!", "success")
            return redirect(url_for("users.list_users"))
        else:
            # Salva os dados e erros na sessão
            session['form_data'] = {
                'email': email,
                'role': role,
                'tenant_id': tenant_id
            }
            session['form_errors'] = result.get('errors', {})
            
            for field, error in result.get('errors', {}).items():
                flash(f"{error}", "error")
            
            return redirect(url_for("users.create_user"))

@user_bp.route("/users/<uuid:user_id>/edit", methods=["GET"])
@login_required
def edit_user_page(user_id):
    try:
        user = UserService.get_user(user_id)
        tenants = TenantService.list_tenants()
        return render_template(
            "users/edit.html",
            user=user,
            tenants=tenants
        )
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("users.list_users"))


@user_bp.route("/users/<uuid:user_id>/edit", methods=["POST"])
@login_required
def update_user(user_id):
    try:
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "").strip()
        tenant_id = request.form.get("tenant_id", "").strip()
        
        # Se tenant_id for vazio, converte para None
        if tenant_id == "":
            tenant_id = None
        
        # Validação básica
        errors = {}
        if not email:
            errors['email'] = "E-mail é obrigatório"
        if not role:
            errors['role'] = "Função é obrigatória"
        
        if errors:
            for field, error in errors.items():
                flash(f"{error}", "error")
            return redirect(url_for("users.edit_user_page", user_id=user_id))

        data = {
            "email": email,
            "role": role,
            "tenant_id": tenant_id
        }

        result = UserService.update_user(user_id, data)
        
        if result.get('success', True):  # Assumindo que update_user também retorna um dicionário
            flash("Usuário atualizado com sucesso!", "success")
        else:
            for field, error in result.get('errors', {}).items():
                flash(f"{error}", "error")
            return redirect(url_for("users.edit_user_page", user_id=user_id))
            
    except Exception as e:
        flash(f"Erro ao atualizar usuário: {str(e)}", "error")
    
    return redirect(url_for("users.list_users"))


@user_bp.route("/users/<uuid:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    try:
        UserService.delete_user(user_id)
        flash("Usuário excluído com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir usuário: {str(e)}", "error")
    
    return redirect(url_for("users.list_users"))