from app.repositories.hotspot_user_repository import HotspotUserRepository


class HotspotUserService:


    @staticmethod
    def create_user(data):

        return HotspotUserRepository.create(data)


    @staticmethod
    def list_users():

        return HotspotUserRepository.get_all()


    @staticmethod
    def get_user(user_id):

        user = HotspotUserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário hotspot não encontrado")

        return user


    @staticmethod
    def update_user(user_id, data):

        user = HotspotUserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário hotspot não encontrado")

        for key, value in data.items():
            setattr(user, key, value)

        return HotspotUserRepository.save(user)


    @staticmethod
    def delete_user(user_id):

        user = HotspotUserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário hotspot não encontrado")

        HotspotUserRepository.delete(user)