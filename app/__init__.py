from flask import Flask, g
from datetime import datetime

from app.utils.filters import datetime_br

# Extensions
from .extensions import db, migrate, jwt, login_manager
from .config import Config

# Models
from app.models.user import User

# Blueprints
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.tenant_routes import tenant_bp
from app.routes.plan_routes import plan_bp
from app.routes.router_routes import router_bp
from app.routes.hotspot_user_routes import hotspot_user_bp
from app.routes.hotspot_template_routes import hotspot_template_bp
from app.routes.bypass_device_routes import bypass_device_bp
from app.routes.ip_pool_routes import ip_pool_bp
from app.routes.active_session_routes import active_session_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.error_test_routes import error_test_bp

from app.cli import register_cli

# Utils
from app.utils.logger import setup_logging
from app.utils.error_handlers import register_error_handlers


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------- EXTENSIONS --------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_cli(app)
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"
    login_manager.login_message = "Faça login para acessar esta página"
    # -------------------- USER LOADER --------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # -------------------- LOGGING --------------------
    setup_logging(app)
    app.logger.info("Aplicação iniciada")

    # -------------------- ERROR HANDLERS --------------------
    register_error_handlers(app)

    # -------------------- BLUEPRINTS --------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(router_bp)
    app.register_blueprint(hotspot_user_bp)
    app.register_blueprint(hotspot_template_bp)
    app.register_blueprint(bypass_device_bp)
    app.register_blueprint(ip_pool_bp)
    app.register_blueprint(active_session_bp)

    # blueprint apenas para testar erros
    app.register_blueprint(error_test_bp)

    app.jinja_env.filters["datetime_br"] = datetime_br
    # -------------------- CONTEXT PROCESSOR --------------------
    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now().year}

    # -------------------- BEFORE REQUEST --------------------
    @app.before_request
    def before_request():
        """
        Define variáveis globais da requisição.
        Muito útil para arquitetura multi-tenant.
        """

        g.current_user = None
        g.tenant_id = None

        from flask_login import current_user

        if current_user.is_authenticated:
            g.current_user = current_user
            g.tenant_id = current_user.tenant_id

    return app