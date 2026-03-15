from app.extensions import db
from app.models.hotspot_user import HotspotUser


class HotspotUserRepository:


    @staticmethod
    def create(data):

        user = HotspotUser(**data)

        db.session.add(user)
        db.session.commit()

        return user


    @staticmethod
    def get_all():

        return HotspotUser.query.all()


    @staticmethod
    def get_by_id(user_id):

        return HotspotUser.query.get(user_id)


    @staticmethod
    def save(user):

        db.session.add(user)
        db.session.commit()

        return user


    @staticmethod
    def delete(user):

        db.session.delete(user)
        db.session.commit()