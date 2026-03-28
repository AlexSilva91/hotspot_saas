from flask import request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.controller.base_controller import BaseController
from app.services.user_service import UserService
from app.services.tenant_service import TenantService

class UserController:
    
    @staticmethod
    def list():
        """Listar usuários"""
        result = UserService.list()
        users = result.get("data", [])
        
        tenants_result = TenantService.list()
        tenants = tenants_result.get("data", [])
        
        form_data = session.pop("form_data", {})
        form_errors = session.pop("form_errors", {})
        
        return {
            "users": users,
            "tenants": tenants,
            "form_data": form_data,
            "form_errors": form_errors
        }
    
    @staticmethod
    def create():
        """Criar usuário"""
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
    
    @staticmethod
    def update(user_id):
        """Atualizar usuário"""
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
    
    @staticmethod
    def delete(user_id):
        """Deletar usuário"""
        result = UserService.delete(user_id)
        
        return BaseController.handle_result(
            result=result,
            success_message="Usuário excluído com sucesso!",
            error_default="Erro ao excluir usuário",
            redirect_to="users.list_users"
        )