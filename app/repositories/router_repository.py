from app.extensions import db
from app.models.router import Router


class RouterRepository:

    @staticmethod
    def create(data):

        router = Router(**data)

        db.session.add(router)
        db.session.commit()

        return router


    @staticmethod
    def get_all():

        return Router.query.all()


    @staticmethod
    def get_by_id(router_id):

        return Router.query.get(router_id)


    @staticmethod
    def delete(router):

        db.session.delete(router)
        db.session.commit()