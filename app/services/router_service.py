from app.repositories.router_repository import RouterRepository


class RouterService:

    @staticmethod
    def create_router(data):

        return RouterRepository.create(data)


    @staticmethod
    def list_routers():

        return RouterRepository.get_all()


    @staticmethod
    def get_router(router_id):

        router = RouterRepository.get_by_id(router_id)

        if not router:
            raise Exception("Router não encontrado")

        return router


    @staticmethod
    def update_router(router_id, data):

        router = RouterRepository.get_by_id(router_id)

        if not router:
            raise Exception("Router não encontrado")

        return RouterRepository.update(router, data)


    @staticmethod
    def delete_router(router_id):

        router = RouterRepository.get_by_id(router_id)

        if not router:
            raise Exception("Router não encontrado")

        RouterRepository.delete(router)