from flask import g
from app.services.base_service import BaseService
from app.repositories.radius.radius_reply_repository import RadiusReplyRepository
from app.extensions import db

class RadiusReplyService(BaseService):
    repository = RadiusReplyRepository
    not_found_message = "Atributo RADIUS não encontrado"
    allowed_update_fields = ["username", "attribute", "value", "op"]

    @classmethod
    def create(cls, data):
        """Cria um novo atributo de resposta"""
        if 'tenant_id' not in data or not data['tenant_id']:
            data['tenant_id'] = g.current_user.tenant_id
        if 'op' not in data:
            data['op'] = ':='

        return super().create(data)

    @classmethod
    def create_or_update_rate_limit(cls, username, rate_limit, tenant_id=None):
        """Cria ou atualiza o rate limit de um usuário"""
        if not tenant_id:
            tenant_id = g.current_user.tenant_id

        existing = cls.repository.get_by_username_and_attribute(
            username, "Mikrotik-Rate-Limit"
        )

        if existing:
            existing.value = rate_limit
            db.session.commit()
            return {"success": True, "data": existing}
        else:
            return cls.create({
                'username': username,
                'attribute': 'Mikrotik-Rate-Limit',
                'value': rate_limit,
                'tenant_id': tenant_id
            })

    @classmethod
    def get_user_attributes(cls, username):
        """Retorna todos os atributos de um usuário"""
        attributes = cls.repository.get_by_username(username)
        return {"success": True, "data": attributes}