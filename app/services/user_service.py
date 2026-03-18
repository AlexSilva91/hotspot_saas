from flask import g
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
import re

from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.decorators.plan_limit import enforce_plan_limits

GLOBAL_ROLES = {"ADMIN", "MANAGER"}


class UserService(BaseService):
    repository = UserRepository
    not_found_message = "Usuário não encontrado"
    allowed_update_fields = ["email", "password_hash", "role", "tenant_id", "active"]

    @staticmethod
    def validate_email(email, user_id=None):
        if not email:
            return False, "E-mail é obrigatório"

        regex = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(regex, email):
            return False, "Formato inválido"

        existing = UserRepository.get_by_email(email)
        if existing and str(existing.id) != str(user_id):
            return False, "E-mail já cadastrado"

        return True, ""

    @classmethod
    @enforce_plan_limits(resource="user")
    def create(cls, data):
        # Aplica regra de tenant para não-admins
        if g.current_user.role.value not in GLOBAL_ROLES:
            data["tenant_id"] = g.current_user.tenant_id

        # Valida email
        valid, msg = cls.validate_email(data.get("email"))
        if not valid:
            return {"success": False, "errors": {"email": msg}}

        try:
            # Usa o método create do BaseService
            return super().create(data)
        except IntegrityError as e:
            from app.extensions import db
            db.session.rollback()
            if isinstance(e.orig, UniqueViolation):
                return {"success": False, "errors": {"email": "E-mail já cadastrado"}}
            return {"success": False, "errors": {"general": "Erro no banco de dados"}}

    @classmethod
    def list(cls):
        # Filtra por tenant para não-admins
        if g.current_user.role.value not in GLOBAL_ROLES:
            users = cls.repository.get_by_tenant(g.current_user.tenant_id)
            return {"success": True, "data": users}

        # Admins veem tudo
        return super().list()

    @classmethod
    def update(cls, obj_id, data):
        # Busca o usuário
        obj = cls.repository.get_by_id(obj_id)

        if not obj:
            return {
                "success": False,
                "errors": {"not_found": cls.not_found_message}
            }

        # Verifica permissão para não-admins
        if g.current_user.role.value not in GLOBAL_ROLES:
            if str(obj.tenant_id) != str(g.current_user.tenant_id):
                return {"success": False, "errors": {"permission": "Acesso negado"}}

        # Converte password para password_hash se necessário
        if "password" in data:
            from werkzeug.security import generate_password_hash
            data["password_hash"] = generate_password_hash(data.pop("password"))

        try:
            # Usa o método update do BaseService
            return super().update(obj_id, data)
        except IntegrityError as e:
            from app.extensions import db
            db.session.rollback()
            if isinstance(e.orig, UniqueViolation):
                return {"success": False, "errors": {"email": "E-mail já cadastrado"}}
            return {"success": False, "errors": {"general": "Erro no banco de dados"}}