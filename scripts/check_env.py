#!/usr/bin/env python
"""
Script para verificar se todas as variáveis de ambiente estão configuradas corretamente
Uso: python scripts/check_env.py
"""
import os
import sys
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

def check_env():
    """Verifica todas as variáveis de ambiente necessárias"""
    
    required_vars = {
        'SECRET_KEY': 'Chave secreta do Flask',
        'DATABASE_URL': 'URL do banco de dados PostgreSQL',
        'JWT_SECRET_KEY': 'Chave secreta para JWT',
    }
    
    optional_vars = {
        'FLASK_ENV': 'development',
        'USE_RADIUS': 'False',
        'HYBRID_MODE': 'True',
        'LOG_LEVEL': 'INFO',
    }
    
    print("\n🔍 VERIFICANDO CONFIGURAÇÃO DO AMBIENTE")
    print("=" * 60)
    
    # Verifica variáveis obrigatórias
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"  ❌ {var}: {description} (não configurada)")
        else:
            # Esconde partes sensíveis
            if 'KEY' in var or 'SECRET' in var:
                masked = value[:8] + '...' if len(value) > 8 else '***'
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value[:50]}...")
    
    if missing:
        print("\n❌ VARIÁVEIS OBRIGATÓRIAS FALTANDO:")
        for m in missing:
            print(m)
        return False
    
    # Verifica variáveis opcionais
    print("\n📋 CONFIGURAÇÕES OPCIONAIS:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"  📌 {var}: {value}")
    
    # Verifica configurações RADIUS
    use_radius = os.getenv('USE_RADIUS', 'False').lower() in ('true', '1', 't')
    radius_db = os.getenv('RADIUS_DB_URI')
    
    if use_radius:
        print("\n🔥 CONFIGURAÇÃO RADIUS ATIVADA:")
        if radius_db:
            print(f"  ✅ RADIUS_DB_URI: configurada")
        else:
            print(f"  ⚠️  RADIUS_DB_URI: usando mesmo banco do DATABASE_URL")
    else:
        print("\n🔥 RADIUS DESATIVADO (USE_RADIUS=False)")
    
    print("\n✅ AMBIENTE CONFIGURADO CORRETAMENTE")
    return True

if __name__ == "__main__":
    if not check_env():
        sys.exit(1)
    sys.exit(0)