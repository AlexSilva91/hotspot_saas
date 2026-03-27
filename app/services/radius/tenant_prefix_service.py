# app/services/radius/tenant_prefix_service.py

import uuid
from flask import g, has_request_context

class TenantPrefixService:
    """
    Gerencia prefixo de tenant nos usernames do RADIUS.
    Formato: {tenant_prefix}:{original_username}
    """
    
    SEPARATOR = ":"
    PREFIX_LENGTH = 8
    
    @classmethod
    def get_tenant_prefix(cls, tenant_id=None):
        """
        Extrai o prefixo de um tenant_id.
        
        Args:
            tenant_id: UUID do tenant (opcional, usa do usuário logado)
        
        Returns:
            str: Prefixo de 8 caracteres ou None
        """
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
        
        Args:
            username: Nome original do usuário
            tenant_id: UUID do tenant (opcional)
        
        Returns:
            str: Username com prefixo
        """
        if not username:
            return username
        
        prefix = cls.get_tenant_prefix(tenant_id)
        if not prefix or cls.SEPARATOR in username:
            return username
        
        return f"{prefix}{cls.SEPARATOR}{username}"
    
    @classmethod
    def decode(cls, username):
        """
        Remove prefixo do username.
        
        Args:
            username: Username com prefixo
        
        Returns:
            str: Username original sem prefixo
        """
        if not username or cls.SEPARATOR not in username:
            return username
        
        return username.split(cls.SEPARATOR, 1)[1]
    
    @classmethod
    def get_prefix(cls, username):
        """
        Extrai apenas o prefixo do username.
        
        Args:
            username: Username com prefixo
        
        Returns:
            str: Prefixo ou None
        """
        if not username or cls.SEPARATOR not in username:
            return None
        return username.split(cls.SEPARATOR, 1)[0]
    
    @classmethod
    def get_like_pattern(cls, tenant_id=None):
        """
        Retorna padrão LIKE para filtro por tenant.
        
        Args:
            tenant_id: UUID do tenant (opcional)
        
        Returns:
            str: Padrão LIKE ou None
        """
        prefix = cls.get_tenant_prefix(tenant_id)
        if not prefix:
            return None
        return f"{prefix}{cls.SEPARATOR}%"