import uuid

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.tenant import Tenant
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
import re


class UserService:

    @staticmethod
    def validate_email(email):
        """Valida formato do email"""
        if not email:
            return False, "E-mail é obrigatório"
        
        # Regex para validação básica de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Formato de e-mail inválido"
        
        # Verifica se já existe usuário com este email
        existing_user = UserRepository.get_by_email(email)
        if existing_user:
            return False, "Já existe um usuário com este e-mail"
        
        return True, ""

    @staticmethod
    def validate_password(password):
        """Valida a senha"""
        if not password:
            return False, "Senha é obrigatória"
        
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        return True, ""

    @staticmethod
    def validate_role(role):
        """Valida a função do usuário"""
        if not role:
            return False, "Função é obrigatória"
        
        # Lista de funções permitidas
        allowed_roles = ['admin', 'manager', 'user', 'viewer']
        if role not in allowed_roles:
            return False, f"Função inválida. Deve ser uma das: {', '.join(allowed_roles)}"
        
        return True, ""

    @staticmethod
    def validate_tenant_id(tenant_id):
        """Valida se o tenant existe (quando fornecido)"""
        if tenant_id and tenant_id.strip():
            from app.services.tenant_service import TenantService
            tenant = TenantService.get_tenant(uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id)
            if not tenant:
                return False, "Empresa não encontrada"
        
        return True, ""

    @staticmethod
    def validate_create_data(data):
        """
        Valida todos os campos antes de criar o usuário
        Retorna (is_valid, errors_dict)
        """
        errors = {}
        
        # Valida email
        email_valid, email_error = UserService.validate_email(data.get('email'))
        if not email_valid:
            errors['email'] = email_error
        
        # Valida senha
        password_valid, password_error = UserService.validate_password(data.get('password_hash'))
        if not password_valid:
            errors['password'] = password_error
        
        # Valida função
        role_valid, role_error = UserService.validate_role(data.get('role'))
        if not role_valid:
            errors['role'] = role_error
        
        # Valida tenant_id (opcional, mas se fornecido deve existir)
        tenant_valid, tenant_error = UserService.validate_tenant_id(data.get('tenant_id'))
        if not tenant_valid:
            errors['tenant_id'] = tenant_error
        
        return len(errors) == 0, errors

    @staticmethod
    def create_user(data):
        """
        Cria um novo usuário com validação completa
        """
        # Valida os dados
        is_valid, errors = UserService.validate_create_data(data)
        
        if not is_valid:
            # Retorna um dicionário com os erros para serem exibidos no frontend
            return {
                'success': False,
                'errors': errors,
                'message': 'Erro de validação nos campos'
            }
        
        try:
            # Converte tenant_id vazio para None
            if 'tenant_id' in data and (not data['tenant_id'] or data['tenant_id'].strip() == ''):
                data['tenant_id'] = None
            
            # Cria o usuário
            user = UserRepository.create(data)
            
            return {
                'success': True,
                'user': user,
                'message': 'Usuário criado com sucesso'
            }
            
        except IntegrityError as e:
            db.session.rollback()
            if isinstance(e.orig, UniqueViolation):
                return {
                    'success': False,
                    'errors': {'email': 'Já existe um usuário com este e-mail'},
                    'message': 'Erro de violação de unicidade'
                }
            return {
                'success': False,
                'errors': {'general': 'Erro ao criar usuário no banco de dados'},
                'message': 'Erro de integridade no banco de dados'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'errors': {'general': str(e)},
                'message': 'Erro inesperado ao criar usuário'
            }

    @staticmethod
    def list_users():
        return UserRepository.get_all()

    @staticmethod
    def get_user(user_id):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        return user

    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        for key, value in data.items():
            setattr(user, key, value)

        return UserRepository.save(user)

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        UserRepository.delete(user)