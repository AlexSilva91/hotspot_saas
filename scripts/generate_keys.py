#!/usr/bin/env python
"""
Script para gerar chaves seguras para o .env
Uso: python scripts/generate_keys.py
"""
import secrets
import os

def generate_keys():
    """Gera chaves seguras para SECRET_KEY e JWT_SECRET_KEY"""
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    
    print("\n🔐 CHAVES GERADAS PARA .env:")
    print("=" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret_key}")
    print("=" * 50)
    print("\n⚠️  Copie estas chaves para seu arquivo .env")
    print("Nunca compartilhe ou commite estas chaves!\n")
    
    return secret_key, jwt_secret_key

if __name__ == "__main__":
    generate_keys()