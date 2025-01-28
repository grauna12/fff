from enum import Enum
from typing import Dict, List, Any
import streamlit as st
import logging


logger = logging.getLogger(__name__)

class UserRole(Enum):
    DIRETOR = "diretor"
    GESTOR_COMERCIAL = "gestor_comercial"
    GESTOR_POSVENDA = "gestor_posvenda"
    VENDEDOR = "vendedor"
    ADM_CNHC = "adm_cnhc"

# Definição de acesso aos dashboards por perfil
ROLE_ACCESS = {
    UserRole.DIRETOR.value: [
        "Dashboard",
        "Comercial",
        "Carros",
        "Yamaha",
        "Gsv",
        "Adm"
    ],
    UserRole.GESTOR_COMERCIAL.value: [
        "Dashboard",
        "Comercial",
        "Carros",
        "Yamaha"
    ],
    UserRole.GESTOR_POSVENDA.value: [
        "Dashboard",
        "Gsv",
        "Yamaha"
    ],
    UserRole.VENDEDOR.value: [
        "Dashboard",
        "Carros",
        "Yamaha"
    ],
    UserRole.ADM_CNHC.value: [
        "Dashboard",
        "Adm"
    ]
}

def get_user_role(email: str) -> str:
    """
    Obtém o papel do usuário do banco de dados.
    """
    try:
        conn = get_database()
        if conn:
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
        logger.error(f"Erro ao obter papel do usuário: {e}")
        return None
    finally:
        if conn:
            conn.close()

def filter_accessible_components(components: Dict[str, Any], user_email: str) -> Dict[str, Any]:
    """
    Filtra os componentes baseado no papel do usuário.
    """
    try:
        role = get_user_role(user_email)
        if not role:
            logger.error(f"Papel não encontrado para usuário: {user_email}")
            return {}

        allowed_components = ROLE_ACCESS.get(role, [])
        return {name: comp for name, comp in components.items() if name in allowed_components}
    except Exception as e:
        logger.error(f"Erro ao filtrar componentes: {e}")
        return {}

def check_component_access(component_name: str, user_email: str) -> bool:
    """
    Verifica se o usuário tem acesso a um componente específico.
    """
    try:
        role = get_user_role(user_email)
        if not role:
            return False
        return component_name in ROLE_ACCESS.get(role, [])
    except Exception as e:
        logger.error(f"Erro ao verificar acesso ao componente: {e}")
        return False