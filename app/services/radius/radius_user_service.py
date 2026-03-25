from flask import g
from app.services.base_service import BaseService
from app.repositories.radius.radius_user_repository import RadiusUserRepository
from app.repositories.radius.radius_reply_repository import RadiusReplyRepository
from app.services.radius.radius_reply_service import RadiusReplyService
from app.extensions import db

class RadiusUserService(BaseService):
    repository = RadiusUserRepository
    not_found_message = "Usuário RADIUS não encontrado"
    allowed_update_fields = ["username", "value", "attribute", "op"]

    @classmethod
    def create(cls, data):
        """Cria um novo usuário no radcheck"""
        # Garante tenant_id do contexto
        if 'tenant_id' not in data or not data['tenant_id']:
            data['tenant_id'] = g.current_user.tenant_id

        # Define valores padrão
        if 'attribute' not in data:
            data['attribute'] = 'Cleartext-Password'
        if 'op' not in data:
            data['op'] = ':='

        return super().create(data)

    @classmethod
    def create_with_rate_limit(cls, username, password, rate_limit=None, tenant_id=None):
        """Cria usuário com senha e opcionalmente limite de banda"""
        if not tenant_id:
            tenant_id = g.current_user.tenant_id

        # Cria usuário
        user_result = cls.create({
            'username': username,
            'value': password,
            'tenant_id': tenant_id
        })

        if not user_result['success']:
            return user_result

        # Cria rate limit se especificado
        if rate_limit:
            rate_result = RadiusReplyService.create_or_update_rate_limit(
                username, rate_limit, tenant_id
            )
            if not rate_result['success']:
                # Rollback? Opcional
                pass

        return user_result

    @classmethod
    def update_password(cls, username, new_password):
        """Atualiza a senha de um usuário RADIUS"""
        user = cls.repository.get_by_username(username)
        if not user:
            return {"success": False, "errors": {"not_found": cls.not_found_message}}

        user.value = new_password
        db.session.commit()
        return {"success": True, "data": user}

    @classmethod
    def delete_with_replies(cls, username):
        """Remove usuário e todos os seus atributos (radreply)"""
        # Remove replies primeiro
        RadiusReplyRepository.delete_by_username(username)
        # Remove user
        count = cls.repository.delete_by_username(username)
        return {"success": True, "deleted_count": count}