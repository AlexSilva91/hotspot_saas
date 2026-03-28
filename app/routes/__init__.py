from app.routes.user_routes.user_routes import user_bp
from app.routes.tenant_routes.tenant_routes import tenant_bp
from app.routes.router_routes.router_routes import router_bp
from app.routes.plan_routes.plan_routes import plan_bp
from app.routes.ip_pool_routes.ip_pool_routes import ip_pool_bp
from app.routes.hotspot_user_routes.hotspot_user_routes import hotspot_user_bp
from app.routes.hotspot_template_routes.hotspot_template_routes import hotspot_template_bp
from app.routes.bypass_device_routes.bypass_device_routes import bypass_device_bp
from app.routes.active_session_routes.active_session_routes import active_session_bp
from app.routes.dashboard_routes.dashboard_routes import dashboard_bp
from app.routes.landing_routes.landing_routes import landing_bp
from app.routes.auth_routes.auth_routes import auth_bp
from app.routes.error_test_routes.error_test_routes import error_test_bp

def init_routes(app):
    """Registra todos os blueprints no app"""
    app.register_blueprint(user_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(router_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(ip_pool_bp)
    app.register_blueprint(hotspot_user_bp)
    app.register_blueprint(hotspot_template_bp)
    app.register_blueprint(bypass_device_bp)
    app.register_blueprint(active_session_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(error_test_bp)