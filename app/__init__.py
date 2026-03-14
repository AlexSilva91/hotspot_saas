from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from app.routes.plan_routes import plan_bp
from app.routes.router_routes import router_bp
from app.routes.tenant_routes import tenant_bp
from app.routes.user_routes import user_bp

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(plan_bp)
    app.register_blueprint(router_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(user_bp)

    return app