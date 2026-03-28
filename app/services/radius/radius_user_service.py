# app/services/radius/radius_user_service.py
from flask import g, current_app
from app.services.base_service import BaseService
from app.repositories.radius.radius_user_repository import RadiusUserRepository
from app.repositories.radius.radius_reply_repository import RadiusReplyRepository
from app.services.radius.radius_reply_service import RadiusReplyService
from app.extensions import db


class RadiusUserService(BaseService):
    repository = RadiusUserRepository
    not_found_message = "Usuário RADIUS não encontrado"
    allowed_update_fields = ["username", "value", "attribute", "op", "is_active"]

    @classmethod
    def create(cls, data):
        """Cria um novo usuário no radcheck"""
        # Define valores padrão
        if 'attribute' not in data:
            data['attribute'] = 'Cleartext-Password'
        if 'op' not in data:
            data['op'] = ':='
        if 'is_active' not in data:
            data['is_active'] = True

        return super().create(data)

    @classmethod
    def create_with_rate_limit(cls, username, password, rate_limit=None, tenant_id=None):
        """Cria usuário com senha e opcionalmente limite de banda
        
        Args:
            username: Nome do usuário
            password: Senha
            rate_limit: Limite de banda (opcional)
            tenant_id: UUID do tenant (opcional, se não informado usa do contexto)
        """
        # Se não passou tenant_id, tenta pegar do contexto
        if not tenant_id:
            from flask import g
            if hasattr(g, 'current_user') and g.current_user:
                tenant_id = g.current_user.tenant_id
        
        # Cria usuário com tenant_id
        user_data = {
            'username': username,
            'value': password,
            'tenant_id': tenant_id
        }
        
        user_result = cls.create(user_data)

        if not user_result['success']:
            return user_result

        # Cria rate limit se especificado
        if rate_limit:
            rate_result = RadiusReplyService.create_or_update_rate_limit(
                username, rate_limit, tenant_id
            )
            if not rate_result['success']:
                if current_app.config.get('HYBRID_MODE', True):
                    current_app.logger.warning(
                        f"RADIUS: erro ao criar rate limit para {username}: {rate_result.get('errors')}"
                    )

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

    @classmethod
    def get_user_rate_limit(cls, username):
        """Retorna o rate limit do usuário se existir"""
        rate_limit = RadiusReplyRepository.get_rate_limit(username)
        return {"success": True, "data": rate_limit}