from flask import g


def tenant_filter(query):

    """
    Aplica filtro automático de tenant nas queries
    """

    if hasattr(query.column_descriptions[0]["entity"], "tenant_id"):

        return query.filter_by(tenant_id=g.tenant_id)

    return query