
import logging
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Tuple
# Adiciona o diretório raiz ao PYTHONPATH
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import get_database

logger = logging.getLogger(__name__)

def validate_user(email: str, senha: str) -> Tuple[bool, str]:
    """
    Valida o usuário com base no email e senha fornecidos.
    Retorna uma tupla (success, message).
    """
    try:
        conn = get_database()
        if not conn:
            return False, "Erro ao conectar ao banco de dados."
        
        with conn.cursor() as cursor:
            query = """
                SELECT u.email, u.senha, u.nome, r.role_name 
                FROM usuarios u
                JOIN user_roles r ON u.role_id = r.id
                WHERE u.email = %s
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user:
                if check_password_hash(user['senha'], senha):
                    return True, "Login bem-sucedido!"
                else:
                    return False, "Email ou senha incorretos."
            else:
                return False, "Email ou senha incorretos."
    
    except Exception as e:
        logger.error(f"Erro ao validar usuário: {str(e)}")
        return False, f"Erro ao validar usuário: {str(e)}"
    
    finally:
        if conn:
            conn.close()

def create_user(email: str, senha: str, nome: str, role: str) -> Tuple[bool, str]:
    """
    Cria um novo usuário com email, senha criptografada, nome e role.
    
    Args:
        email (str): Email do usuário
        senha (str): Senha do usuário (será criptografada)
        nome (str): Nome completo do usuário
        role (str): Papel do usuário (deve existir na tabela user_roles)
    
    Returns:
        Tuple[bool, str]: (Sucesso, Mensagem)
    """
    try:
        conn = get_database()
        if not conn:
            return False, "Erro ao conectar ao banco de dados."
        
        with conn.cursor() as cursor:
            # Verificar se o email já está em uso
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email já está em uso."
            
            # Verificar se o role existe
            cursor.execute("SELECT id FROM user_roles WHERE role_name = %s", (role,))
            role_data = cursor.fetchone()
            if not role_data:
                return False, f"Role '{role}' não encontrado no sistema."
            
            role_id = role_data['id']
            
            # Criptografar a senha
            hashed_password = generate_password_hash(senha)
            
            # Inserir o novo usuário
            query = """
                INSERT INTO usuarios (email, senha, nome, role_id) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (email, hashed_password, nome, role_id))
            conn.commit()
            
            logger.info(f"Usuário criado com sucesso: {email}")
            return True, "Usuário criado com sucesso!"
    
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        return False, f"Erro ao criar usuário: {str(e)}"
    
    finally:
        if conn:
            conn.close()

def get_user_role(email: str) -> str:
    """
    Obtém o papel (role) do usuário.
    
    Args:
        email (str): Email do usuário
    
    Returns:
        str: Nome do role ou None se não encontrado
    """
    try:
        conn = get_database()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            query = """
                SELECT r.role_name 
                FROM usuarios u
                JOIN user_roles r ON u.role_id = r.id
                WHERE u.email = %s
            """
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result['role_name'] if result else None
    
    except Exception as e:
        logger.error(f"Erro ao obter role do usuário: {str(e)}")
        return None
    
    finally:
        if conn:
            conn.close()

create_user("vendedor", "12345678", "vendedor", "vendedor")