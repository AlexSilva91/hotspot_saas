from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, jwt
from werkzeug.exceptions import HTTPException

from app.routes.plan_routes import plan_bp
from app.routes.router_routes import router_bp
from app.routes.tenant_routes import tenant_bp
from app.routes.user_routes import user_bp

from app.utils.logger import setup_logging


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Logging
    setup_logging(app)
    app.logger.info("Aplicação iniciada")

    # Blueprints
    app.register_blueprint(plan_bp)
    app.register_blueprint(router_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(user_bp)

    # Global Exception Handler
    @app.errorhandler(Exception)
    def handle_exception(e):

        if isinstance(e, HTTPException):
            return e

        app.logger.exception("Erro não tratado")

        return {
            "error": "Erro interno do servidor"
        }, 500

    return app