# app/middleware/tenant_middleware.py
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

    # PRIORIDADE 1: Entidade com tenant_id direto (RADIUS models agora têm)
    if hasattr(entity, "tenant_id"):
        return query.filter(entity.tenant_id == current_user.tenant_id)

    # Entidade Tenant
    if entity == Tenant:
        return query.filter(Tenant.id == current_user.tenant_id)

    # Caso especial: Plan → Tenant
    if entity.__name__ == "Plan":
        alias = aliased(Tenant)
        return query.join(alias, alias.plan_id == entity.id).filter(alias.id == current_user.tenant_id)

    # FALLBACK: Para modelos que ainda usam prefixo (durante migração)
    if hasattr(entity, "username") and entity.__name__ in ['RadiusUser', 'RadiusReply', 'RadiusAccounting', 'RadiusPostAuth']:
        from app.services.radius.tenant_prefix_service import TenantPrefixService
        like_pattern = TenantPrefixService.get_like_pattern(current_user.tenant_id)
        if like_pattern:
            return query.filter(entity.username.like(like_pattern))
        return query.filter(False)

    # Verifica FKs relacionadas com tenant_id
    if hasattr(entity, "__mapper__"):
        for rel in entity.__mapper__.relationships.values():
            rel_class = rel.mapper.class_
            if hasattr(rel_class, "tenant_id"):
                alias_name = f"{rel_class.__tablename__}_alias"
                alias = aliased(rel_class, name=alias_name)
                return query.join(alias).filter(alias.tenant_id == current_user.tenant_id)

    return query