from app.repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def create_user(data):

        return UserRepository.create(data)


    @staticmethod
    def list_users():

        return UserRepository.get_all()


    @staticmethod
    def get_user(user_id):

        user = UserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        return user


    @staticmethod
    def delete_user(user_id):

        user = UserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        UserRepository.delete(user)