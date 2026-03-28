# app/services/radius/radius_group_reply_service.py
from app.services.base_service import BaseService
from app.repositories.radius.radius_group_reply_repository import RadiusGroupReplyRepository


class RadiusGroupReplyService(BaseService):
    repository = RadiusGroupReplyRepository
    not_found_message = "Atributo de grupo não encontrado"
    allowed_update_fields = ["groupname", "attribute", "value", "op"]

    @classmethod
    def get_group_attributes(cls, groupname):
        """Retorna todos atributos de um grupo"""
        attributes = cls.repository.get_by_group(groupname)
        return {"success": True, "data": attributes}

    @classmethod
    def get_group_rate_limit(cls, groupname):
        """Retorna o rate limit de um grupo"""
        result = cls.repository.get_by_group_and_attribute(groupname, "Mikrotik-Rate-Limit")
        return {"success": True, "data": result.value if result else None}

    @classmethod
    def set_group_rate_limit(cls, groupname, rate_limit):
        """Define rate limit para um grupo"""
        result = cls.repository.create_or_update(groupname, "Mikrotik-Rate-Limit", rate_limit)
        return {"success": True, "data": result}