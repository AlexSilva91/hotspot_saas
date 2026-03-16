from flask_login import current_user
from app.models.user import UserRole
from app.models.tenant import Tenant
from sqlalchemy.orm import aliased

GLOBAL_ROLES = {UserRole.ADMIN, UserRole.MANAGER}

def tenant_filter(query):
    if not current_user.is_authenticated:
        return query

    user_role = current_user.role
    if isinstance(user_role, str):
        from app.models.user import UserRole
        user_role = UserRole(user_role)

    if user_role in GLOBAL_ROLES:
        return query

    entity = query.column_descriptions[0]["entity"]

    # Entidade com tenant_id direto
    if hasattr(entity, "tenant_id"):
        return query.filter(entity.tenant_id == current_user.tenant_id)

    # Entidade Tenant
    if entity == Tenant:
        return query.filter(Tenant.id == current_user.tenant_id)

    # Caso especial: Plan → Tenant
    if entity.__name__ == "Plan":
        alias = aliased(Tenant)
        # Join Plan -> Tenant via Tenant.plan_id, filtra pelo tenant atual
        return query.join(alias, alias.plan_id == entity.id).filter(alias.id == current_user.tenant_id)

    # Verifica FKs relacionadas com tenant_id
    if hasattr(entity, "__mapper__"):
        for rel in entity.__mapper__.relationships.values():
            rel_class = rel.mapper.class_
            if "tenant_id" in rel_class.__table__.columns.keys():
                alias_name = f"{rel_class.__tablename__}_alias"
                alias = aliased(rel_class, name=alias_name)
                return query.join(alias).filter(alias.tenant_id == current_user.tenant_id)

    return query