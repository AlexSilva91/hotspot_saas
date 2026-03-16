import uuid
import re
from flask import g
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from app.repositories.user_repository import UserRepository
from app.extensions import db
from app.models.user import UserRole

# Roles com acesso global
GLOBAL_ROLES = {"ADMIN", "MANAGER"}


class UserService:

    @staticmethod
    def validate_email(email, user_id=None):

        if not email:
            return False, "E-mail é obrigatório"

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Formato de e-mail inválido"

        existing_user = UserRepository.get_by_email(email)
        if existing_user and str(existing_user.id) != str(user_id):
            return False, "Já existe um usuário com este e-mail"

        return True, ""

    @staticmethod
    def validate_role(role):

        if not role:
            return False, "Função é obrigatória"

        allowed_roles = ["ADMIN", "MANAGER", "USER", "VIEWER"]
        role_upper = role.upper()

        if role_upper not in allowed_roles:
            return False, f"Função inválida. Deve ser uma das: {', '.join(allowed_roles)}"

        return True, ""

    @staticmethod
    def validate_tenant_id(tenant_id):
        if tenant_id:
            from app.services.tenant_service import TenantService

            tenant = TenantService.get_tenant(
                uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            )
            if not tenant:
                return False, "Empresa não encontrada"

        return True, ""

    @staticmethod
    def create_user(data):
        # Força tenant_id do usuário logado se não for admin/manager
        if hasattr(g, "current_user") and g.current_user.role not in GLOBAL_ROLES:
            data["tenant_id"] = g.current_user.tenant_id

        errors = {}

        email_valid, email_error = UserService.validate_email(data.get("email"))
        if not email_valid:
            errors["email"] = email_error

        role_valid, role_error = UserService.validate_role(data.get("role"))
        if not role_valid:
            errors["role"] = role_error

        tenant_valid, tenant_error = UserService.validate_tenant_id(data.get("tenant_id"))
        if not tenant_valid:
            errors["tenant_id"] = tenant_error

        if errors:
            return {"success": False, "errors": errors}

        try:
            user = UserRepository.create(data)
            return {"success": True, "user": user}

        except IntegrityError as e:
            db.session.rollback()
            if isinstance(e.orig, UniqueViolation):
                return {"success": False, "errors": {"email": "Já existe um usuário com este e-mail"}}
            return {"success": False, "errors": {"general": "Erro de integridade no banco"}}

    @staticmethod
    def list_users():
        # Filtra por tenant se não for admin/manager
        if hasattr(g, "current_user") and g.current_user.role not in GLOBAL_ROLES:
            return UserRepository.get_all()
        return UserRepository.get_all()

    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise Exception("Usuário não encontrado")

        # Verificação de permissionamento
        if hasattr(g, "current_user") and g.current_user.role not in GLOBAL_ROLES:
            if str(user.tenant_id) != str(g.current_user.tenant_id):
                raise Exception("Você não tem permissão para atualizar este usuário")
            data["tenant_id"] = g.current_user.tenant_id

        errors = {}
        email_valid, email_error = UserService.validate_email(data.get("email"), user_id)
        if not email_valid:
            errors["email"] = email_error

        role_valid, role_error = UserService.validate_role(data.get("role"))
        if not role_valid:
            errors["role"] = role_error

        tenant_valid, tenant_error = UserService.validate_tenant_id(data.get("tenant_id"))
        if not tenant_valid:
            errors["tenant_id"] = tenant_error

        if errors:
            return {"success": False, "errors": errors}

        for key, value in data.items():
            setattr(user, key, value)

        UserRepository.save(user)
        return {"success": True}

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise Exception("Usuário não encontrado")

        # Verificação de permissionamento
        if hasattr(g, "current_user") and g.current_user.role not in GLOBAL_ROLES:
            if str(user.tenant_id) != str(g.current_user.tenant_id):
                raise Exception("Você não tem permissão para deletar este usuário")

        UserRepository.delete(user)