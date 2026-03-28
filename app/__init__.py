from flask import Flask, g, request
from datetime import datetime
import logging

from app.utils.filters import datetime_br
from app.utils.tenant_color import tenant_color

# Extensions
from .extensions import db, migrate, jwt, login_manager
from .config import Config

# Models
from app.models.user import User

# Blueprints
from app.routes import init_routes

# CLI
from app.cli import register_cli
from app.cli.radius.radius_cli import register_radius_cli

# Utils
from app.utils.logger import setup_logging
from app.utils.error_handlers import register_error_handlers
from app.middleware.routes_error_handlers_middleware import register_error_handlers_routes


def create_app():
    """Factory pattern para criar a aplicação Flask"""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Valida configuração (opcional mas recomendado)
    try:
        Config.validate()
    except ValueError as e:
        app.logger.error(f"❌ Erro de configuração: {e}")
        raise e

    # -------------------- EXTENSIONS --------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CLI Commands
    register_cli(app)
    register_radius_cli(app)
    
    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"
    login_manager.login_message = "Faça login para acessar esta página"
    
    # -------------------- USER LOADER --------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # -------------------- LOGGING --------------------
    setup_logging(app)
    app.logger.info("🚀 Aplicação iniciada")
    
    # Log configurações RADIUS
    if app.config.get('USE_RADIUS'):
        app.logger.info(f"🔥 RADIUS ativado (Modo híbrido: {app.config.get('HYBRID_MODE')})")
    else:
        app.logger.info("❌ RADIUS desativado - usando API direta do MikroTik")

    # -------------------- ERROR HANDLERS --------------------
    register_error_handlers(app)
    register_error_handlers_routes(app)

    # -------------------- BLUEPRINTS --------------------
    init_routes(app)

    # -------------------- JINJA FILTERS --------------------
    app.jinja_env.filters["datetime_br"] = datetime_br

    # -------------------- CONTEXT PROCESSORS --------------------
    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now().year}

    @app.context_processor
    def inject_utils():
        return dict(tenant_color=tenant_color)
    
    @app.context_processor
    def inject_radius_config():
        """Injeta configurações RADIUS nos templates"""
        return {
            'use_radius': app.config.get('USE_RADIUS', False),
            'hybrid_mode': app.config.get('HYBRID_MODE', True)
        }

    # -------------------- BEFORE REQUEST --------------------
    @app.before_request
    def before_request():
        """
        Define variáveis globais da requisição.
        Muito útil para arquitetura multi-tenant.
        """
        from flask_login import current_user
        
        g.current_user = None
        g.tenant_id = None

        if current_user.is_authenticated:
            g.current_user = current_user
            g.tenant_id = current_user.tenant_id
        
        # Injeta configuração RADIUS no g para uso nos serviços
        g.use_radius = app.config.get('USE_RADIUS', False)
        g.hybrid_mode = app.config.get('HYBRID_MODE', True)

    # -------------------- AFTER REQUEST --------------------
    @app.after_request
    def after_request(response):
        """Log de requisições (opcional)"""
        if app.debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
            
        app.logger.log(
            log_level,
            f"{request.method} {request.path} -> {response.status_code}"
        )
        return response

    return app