from app.extensions import db
from app.models.ip_pool import IpPool


class IpPoolRepository:

    @staticmethod
    def create(data):

        ip_pool = IpPool(**data)

        db.session.add(ip_pool)
        db.session.commit()

        return ip_pool


    @staticmethod
    def get_all():

        return IpPool.query.all()


    @staticmethod
    def get_by_id(pool_id):

        return IpPool.query.get(pool_id)


    @staticmethod
    def save(pool):

        db.session.add(pool)
        db.session.commit()

        return pool


    @staticmethod
    def delete(pool):

        db.session.delete(pool)
        db.session.commit()