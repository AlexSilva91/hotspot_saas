from app.models.radius.radius_reply import RadiusReply
from app.repositories.base_repository import BaseRepository
from app.extensions import db


class RadiusReplyRepository(BaseRepository):
    model = RadiusReply

    @classmethod
    def get_by_username(cls, username):
        """Busca todos os atributos de um usuário"""
        return cls.model.query.filter_by(username=username).all()

    @classmethod
    def get_by_username_and_attribute(cls, username, attribute):
        """Busca um atributo específico de um usuário"""
        return cls.model.query.filter_by(
            username=username,
            attribute=attribute
        ).first()

    @classmethod
    def get_all(cls):
        """Lista todos os atributos"""
        return cls.model.query.all()

    @classmethod
    def get_rate_limit(cls, username):
        """Retorna o rate limit de um usuário específico"""
        result = cls.get_by_username_and_attribute(username, "Mikrotik-Rate-Limit")
        return result.value if result else None

    @classmethod
    def create_or_update_rate_limit(cls, username, rate_limit):
        """Cria ou atualiza o rate limit de um usuário"""
        existing = cls.get_by_username_and_attribute(username, "Mikrotik-Rate-Limit")
        
        if existing:
            existing.value = rate_limit
            db.session.commit()
            return existing
        else:
            new_reply = cls.model(
                username=username,
                attribute="Mikrotik-Rate-Limit",
                op=":=",
                value=rate_limit
            )
            db.session.add(new_reply)
            db.session.commit()
            return new_reply

    @classmethod
    def delete_rate_limit(cls, username):
        """Remove o rate limit de um usuário"""
        rate_limit = cls.get_by_username_and_attribute(username, "Mikrotik-Rate-Limit")
        if rate_limit:
            db.session.delete(rate_limit)
            db.session.commit()
            return True
        return False

    @classmethod
    def delete_by_username(cls, username):
        """Remove todos os atributos de um usuário"""
        query = cls.model.query.filter_by(username=username)
        count = query.delete()
        db.session.commit()
        return count

    @classmethod
    def get_all_attributes_by_username(cls, username):
        """Retorna todos os atributos de um usuário como dicionário"""
        attributes = cls.get_by_username(username)
        return {
            attr.attribute: attr.value 
            for attr in attributes
        }

    @classmethod
    def get_all_rate_limits(cls):
        """Retorna todos os rate limits configurados"""
        return cls.model.query.filter_by(attribute="Mikrotik-Rate-Limit").all()