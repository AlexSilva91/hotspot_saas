from flask_login import current_user
from app.models import (
    Router,
    User,
    HotspotUser,
    ActiveSession,
    IpPool,
    BypassDevice,
    HotspotTemplate,
)
from app.middleware.tenant_middleware import tenant_filter

class DashboardController:
    
    @staticmethod
    def dashboard():
        """Dashboard principal"""
        tenant = current_user.tenant
        
        routers_query = tenant_filter(Router.query)
        users_query = tenant_filter(User.query)
        hotspot_users_query = tenant_filter(HotspotUser.query)
        active_sessions_query = tenant_filter(ActiveSession.query)
        ip_pools_query = tenant_filter(IpPool.query)
        bypass_devices_query = tenant_filter(BypassDevice.query)
        templates_query = tenant_filter(HotspotTemplate.query)
        
        return {
            "tenant": tenant,
            "routers_count": routers_query.count(),
            "users_count": users_query.count(),
            "hotspot_users_count": hotspot_users_query.count(),
            "active_sessions_count": active_sessions_query.count(),
            "ip_pools_count": ip_pools_query.count(),
            "bypass_devices_count": bypass_devices_query.count(),
            "templates_count": templates_query.count(),
            "routers": routers_query.order_by(Router.created_at.desc()).limit(5).all()
        }