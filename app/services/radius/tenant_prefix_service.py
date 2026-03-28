# app/services/radius/tenant_prefix_service.py
import uuid
from flask import g, has_request_context
from app.extensions import db

class TenantPrefixService:
    """
    Gerencia prefixo de tenant nos usernames do RADIUS.
    AGORA: Mantido apenas para compatibilidade durante migração
    NOVOS USUÁRIOS: Usam tenant_id diretamente
    """
    
    SEPARATOR = ":"
    PREFIX_LENGTH = 8
    
    @classmethod
    def get_tenant_prefix(cls, tenant_id=None):
        """Extrai o prefixo de um tenant_id (mantido para compatibilidade)"""
        if tenant_id is None and has_request_context() and hasattr(g, 'current_user'):
            tenant_id = g.current_user.tenant_id if g.current_user else None
        
        if not tenant_id:
            return None
        
        clean_id = str(tenant_id).replace('-', '')
        return clean_id[:cls.PREFIX_LENGTH]
    
    @classmethod
    def encode(cls, username, tenant_id=None):
        """
        Adiciona prefixo ao username.
        MANTIDO APENAS PARA COMPATIBILIDADE DURANTE MIGRAÇÃO
        """
        if not username:
            return username
        
        # Se já tem separador, retorna como está
        if cls.SEPARATOR in username:
            return username
        
        prefix = cls.get_tenant_prefix(tenant_id)
        if not prefix:
            return username
        
        return f"{prefix}{cls.SEPARATOR}{username}"
    
    @classmethod
    def decode(cls, username):
        """Remove prefixo do username"""
        if not username or cls.SEPARATOR not in username:
            return username
        
        return username.split(cls.SEPARATOR, 1)[1]
    
    @classmethod
    def get_prefix(cls, username):
        """Extrai apenas o prefixo do username"""
        if not username or cls.SEPARATOR not in username:
            return None
        return username.split(cls.SEPARATOR, 1)[0]
    
    @classmethod
    def get_like_pattern(cls, tenant_id=None):
        """
        Retorna padrão LIKE para filtro por tenant.
        MANTIDO APENAS PARA COMPATIBILIDADE DURANTE MIGRAÇÃO
        """
        prefix = cls.get_tenant_prefix(tenant_id)
        if not prefix:
            return None
        return f"{prefix}{cls.SEPARATOR}%"