from app.extensions import db
from app.models.user import User


class UserRepository:

    @staticmethod
    def create(data):

        user = User(**data)

        db.session.add(user)
        db.session.commit()

        return user


    @staticmethod
    def get_all():

        return User.query.all()


    @staticmethod
    def get_by_id(user_id):

        return User.query.get(user_id)


    @staticmethod
    def get_by_email(email):

        return User.query.filter_by(email=email).first()


    @staticmethod
    def delete(user):

        db.session.delete(user)
        db.session.commit()