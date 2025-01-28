import streamlit as st
import os
import sys
from importlib import import_module
import logging
from typing import Dict, Any
from enum import Enum
import time

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import validate_user, create_user
from config.db_config import get_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        "Adm", 
        "Venda"
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
        "Venda"
    ],
    UserRole.ADM_CNHC.value: [
        "Dashboard",
        "Adm"
    ]
}

def apply_custom_style():
    """Aplica estilos customizados globais para a aplicação."""
    st.markdown("""
        <style>
        /* Estilo Global */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar personalizada */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            padding: 1rem 0.5rem;
            border-right: 1px solid #e9ecef;
        }
        
        /* Estilo dos botões da sidebar */
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            background: transparent;
            border: none;
            padding: 0.5rem 1rem;
            text-align: left;
            margin: 0.125rem 0;
            border-radius: 0.375rem;
            transition: all 0.2s;
            color: #1f2937;
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: #e9ecef;
        }
        
        section[data-testid="stSidebar"] .stButton button.active {
            background-color: #e9ecef;
            font-weight: 600;
        }
        
        /* Estilo para o botão Sair */
        section[data-testid="stSidebar"] .logout-button button {
            margin-top: 1rem;
            border: 1px solid #dc2626;
            color: #dc2626;
            font-size: 0.875rem;
            padding: 0.375rem 0.75rem;
        }
        
        section[data-testid="stSidebar"] .logout-button button:hover {
            background-color: #dc2626;
            color: white;
        }
        
        /* Headers e Títulos */
        h1, h2, h3 {
            color: #1f2937;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Loading spinner customizado */
        .stSpinner {
            text-align: center;
            max-width: 50%;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Container principal */
        .main .block-container {
            padding: 2rem 1.5rem;
        }
        
        /* Ajustes de responsividade */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1.5rem 1rem;
            }
            
            section[data-testid="stSidebar"] .stButton button {
                padding: 0.375rem 0.75rem;
                font-size: 0.8125rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def loading_spinner():
    """Exibe um spinner de carregamento personalizado."""
    with st.spinner('Carregando...'):
        time.sleep(0.5)  # Simula um pequeno delay para melhor UX

def get_user_role(email: str) -> str:
    """Obtém o papel do usuário do banco de dados."""
    try:
        logger.info(f"Tentando obter papel do usuário para o email: {email}")
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

def check_component_access(component_name: str, user_email: str) -> bool:
    """Verifica se o usuário tem acesso a um componente específico."""
    try:
        role = get_user_role(user_email)
        if not role:
            return False
        return component_name in ROLE_ACCESS.get(role, [])
    except Exception as e:
        logger.error(f"Erro ao verificar acesso ao componente: {e}")
        return False

def filter_accessible_components(components: Dict[str, Any], user_email: str) -> Dict[str, Any]:
    """Filtra os componentes baseado no papel do usuário."""
    try:
        role = get_user_role(user_email)
        if not role:
            return {}
        allowed_components = ROLE_ACCESS.get(role, [])
        return {name: comp for name, comp in components.items() if name in allowed_components}
    except Exception as e:
        logger.error(f"Erro ao filtrar componentes: {e}")
        return {}

def load_components() -> Dict[str, Any]:
    """Carrega dinamicamente os componentes da pasta components."""
    components = {}
    try:
        with st.spinner("Carregando componentes..."):
            components_path = os.path.join(os.path.dirname(__file__), "components")
            if not os.path.exists(components_path):
                logger.error(f"Diretório de componentes não encontrado: {components_path}")
                return components

            for filename in os.listdir(components_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    try:
                        module_name = filename[:-3]
                        module = import_module(f"components.{module_name}")
                        components[module_name.capitalize()] = getattr(module, module_name)
                    except Exception as e:
                        logger.error(f"Erro ao carregar componente {module_name}: {e}")
                        continue
    except Exception as e:
        logger.error(f"Erro ao carregar componentes: {e}")

    return components

def get_icon_for_page(page_name: str) -> str:
    """Retorna uma string vazia para cada página."""
    return ""

def login_page() -> None:
    """Renderiza a página de login."""
    try:
        st.title("Login")
        logger.info("Renderizando formulário de login")
        
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("Email", placeholder="Digite seu email")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if not email or not senha:
                    st.warning("Por favor, preencha todos os campos.")
                    return
                
                try:
                    with st.spinner("Verificando credenciais..."):
                        success, message = validate_user(email, senha)
                        
                        if success:
                            role = get_user_role(email)
                            if role:
                                st.session_state.update({
                                    'logado': True,
                                    'usuario': email,
                                    'role': role,
                                    'selected_page': "Dashboard"
                                })
                                st.rerun()
                            else:
                                st.error("Erro ao obter perfil do usuário")
                        else:
                            st.error(message)
                            
                except Exception as e:
                    st.error(f"Erro ao tentar fazer login: {str(e)}")
                    
    except Exception as e:
        st.error("Erro ao carregar página de login. Tente novamente mais tarde.")

def render_sidebar(pages: Dict[str, Any]) -> None:
    """Renderiza a sidebar com navegação melhorada."""
    try:
        st.sidebar.markdown("""
            <div style='margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid #e5e7eb;'>
                <h2 style='font-size: 1.25rem; margin-bottom: 0;'>🚗 Dashboard</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if 'usuario' in st.session_state:
            user_email = st.session_state['usuario']
            role = st.session_state.get('role', '')
            
            st.sidebar.markdown(f"""
                <div style='margin-bottom: 1.5rem; padding: 0.75rem; background: white; border-radius: 0.5rem;'>
                    <p style='color: #6b7280; margin-bottom: 0.25rem; font-size: 0.875rem;'>👤 Usuário</p>
                    <p style='font-weight: 500; margin: 0; font-size: 0.875rem;'>{user_email}</p>
                </div>
            """, unsafe_allow_html=True)
            
            selected_page = st.session_state.get('selected_page')
            
            for page_name in pages.keys():
                if check_component_access(page_name, user_email):
                    icon = get_icon_for_page(page_name)
                    button_style = "active" if selected_page == page_name else ""
                    if st.sidebar.button(
                        f"{icon} {page_name}",
                        key=f"nav_{page_name}",
                        help=f"Ir para {page_name}"
                    ):
                        with st.spinner(f"Carregando {page_name}..."):
                            st.session_state['selected_page'] = page_name
                            time.sleep(0.3)  # Pequeno delay para feedback visual
                            st.rerun()
            
            # Botão de logout com classe específica
            st.sidebar.markdown("<div class='logout-button'>", unsafe_allow_html=True)
            if st.sidebar.button("Sair", key="logout_button"):
                with st.spinner("Saindo..."):
                    time.sleep(0.5)  # Pequeno delay para feedback visual
                    st.session_state.clear()
                    st.rerun()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)
            
    except Exception as e:
        st.sidebar.error("❌ Erro ao carregar navegação")

def initialize_session_state() -> None:
    """Inicializa o estado da sessão com valores padrão."""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
    if 'selected_page' not in st.session_state:
        st.session_state['selected_page'] = "Dashboard"

def main() -> None:
    """Função principal com UI melhorada."""
    try:
        apply_custom_style()
        initialize_session_state()
        
        with st.spinner("Iniciando aplicação..."):
            all_components = load_components()
        
        if not st.session_state['logado']:
            login_page()
        else:
            accessible_components = filter_accessible_components(
                all_components, 
                st.session_state['usuario']
            )
            
            render_sidebar(accessible_components)
            
            selected_page = st.session_state.get("selected_page")
            
            if selected_page in accessible_components:
                try:
                    with st.container():
                        st.markdown(f"""
                            <h1 style='font-size: 1.5rem; margin-bottom: 1.5rem;'>
                                {get_icon_for_page(selected_page)} {selected_page}
                            </h1>
                        """, unsafe_allow_html=True)
                        
                        with st.spinner(f"Carregando conteúdo de {selected_page}..."):
                            accessible_components[selected_page]()
                except Exception as e:
                    st.error(f"❌ Erro ao carregar a página {selected_page}")
            elif selected_page not in all_components:
                st.markdown("""
                    <div style='text-align: center; padding: 3rem 0;'>
                        <h1 style='font-size: 1.75rem; margin-bottom: 0.75rem;'>👋 Bem-vindo ao Dashboard!</h1>
                        <p style='color: #6b7280; font-size: 1rem;'>Selecione uma opção no menu lateral para começar.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Você não tem permissão para acessar esta página.")
                
    except Exception as e:
        st.error("❌ Ocorreu um erro ao iniciar a aplicação. Por favor, tente novamente mais tarde.")

if __name__ == "__main__":
    main()