# app/services/radius/radius_usergroup_service.py
from app.services.base_service import BaseService
from app.repositories.radius.radius_usergroup_repository import RadiusUserGroupRepository


class RadiusUserGroupService(BaseService):
    repository = RadiusUserGroupRepository
    not_found_message = "Associação usuário-grupo não encontrada"

    @classmethod
    def get_user_groups(cls, username):
        """Retorna grupos de um usuário"""
        groups = cls.repository.get_by_username(username)
        return {"success": True, "data": groups}

    @classmethod
    def add_user_to_group(cls, username, groupname, priority=1):
        """Adiciona usuário a um grupo"""
        result = cls.repository.add_user_to_group(username, groupname, priority)
        return {"success": True, "data": result}

    @classmethod
    def remove_user_from_group(cls, username, groupname):
        """Remove usuário de um grupo"""
        count = cls.repository.remove_user_from_group(username, groupname)
        return {"success": True, "deleted_count": count}