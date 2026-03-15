from app.repositories.ip_pool_repository import IpPoolRepository


class IpPoolService:


    @staticmethod
    def create_pool(data):

        return IpPoolRepository.create(data)


    @staticmethod
    def list_pools():

        return IpPoolRepository.get_all()


    @staticmethod
    def get_pool(pool_id):

        pool = IpPoolRepository.get_by_id(pool_id)

        if not pool:
            raise Exception("IP Pool não encontrado")

        return pool


    @staticmethod
    def update_pool(pool_id, data):

        pool = IpPoolRepository.get_by_id(pool_id)

        if not pool:
            raise Exception("IP Pool não encontrado")

        for key, value in data.items():
            setattr(pool, key, value)

        return IpPoolRepository.save(pool)


    @staticmethod
    def delete_pool(pool_id):

        pool = IpPoolRepository.get_by_id(pool_id)

        if not pool:
            raise Exception("IP Pool não encontrado")

        IpPoolRepository.delete(pool)