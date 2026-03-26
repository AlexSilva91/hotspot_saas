from flask import g, current_app
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
        # Define valores padrão
        if 'attribute' not in data:
            data['attribute'] = 'Cleartext-Password'
        if 'op' not in data:
            data['op'] = ':='

        return super().create(data)

    @classmethod
    def create_with_rate_limit(cls, username, password, rate_limit=None):
        """Cria usuário com senha e opcionalmente limite de banda"""
        # Cria usuário
        user_result = cls.create({
            'username': username,
            'value': password
        })

        if not user_result['success']:
            return user_result

        # Cria rate limit se especificado
        if rate_limit:
            rate_result = RadiusReplyService.create_or_update_rate_limit(
                username, rate_limit
            )
            if not rate_result['success']:
                # Em modo híbrido, loga o erro mas não falha
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