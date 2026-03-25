import os
from dotenv import load_dotenv
import logging

# Carrega variáveis do .env
load_dotenv()

class Config:
    """Configuração base da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-key-change-in-production")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # RADIUS Configuration
    USE_RADIUS = os.getenv("USE_RADIUS", "False").lower() in ('true', '1', 't')
    HYBRID_MODE = os.getenv("HYBRID_MODE", "True").lower() in ('true', '1', 't')
    RADIUS_DB_URI = os.getenv("RADIUS_DB_URI", None)
    
    # Se RADIUS_DB_URI não for especificado, usa o mesmo banco
    if not RADIUS_DB_URI:
        RADIUS_DB_URI = SQLALCHEMY_DATABASE_URI
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_radius_config(cls):
        """Retorna configurações do RADIUS para uso nos serviços"""
        return {
            'enabled': cls.USE_RADIUS,
            'hybrid_mode': cls.HYBRID_MODE,
            'db_uri': cls.RADIUS_DB_URI
        }
    
    @classmethod
    def validate(cls):
        """Valida configurações críticas"""
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL não configurada no .env")
        
        if cls.USE_RADIUS and not cls.RADIUS_DB_URI:
            raise ValueError("RADIUS_DB_URI não configurada e USE_RADIUS=True")
        
        return True


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    
    # Em produção, use HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    USE_RADIUS = False  # Desativa RADIUS em testes
    LOG_LEVEL = "ERROR"


# Seleciona configuração baseada no ambiente
env = os.getenv("FLASK_ENV", "development")

if env == "production":
    config = ProductionConfig()
elif env == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()