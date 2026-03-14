from app.repositories.router_repository import RouterRepository


class RouterService:

    @staticmethod
    def create_router(data):

        return RouterRepository.create(data)


    @staticmethod
    def list_routers():

        return RouterRepository.get_all()


    @staticmethod
    def delete_router(router_id):

        router = RouterRepository.get_by_id(router_id)

        if not router:
            raise Exception("Router não encontrado")

        RouterRepository.delete(router)