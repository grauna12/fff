import pymysql
import pymysql.cursors
import streamlit as st
from typing import Optional
import logging
import socket

logger = logging.getLogger(__name__)

def get_database() -> Optional[pymysql.connections.Connection]:
    """
    Estabelece uma conexão com o banco de dados MySQL usando as configurações do Streamlit secrets.
    """
    try:
        logger.info("Tentando conexão com o banco de dados...")
        
        # Verificar configurações
        host = st.secrets["general"]["HOST"]
        user = st.secrets["general"]["USER"]
        password = st.secrets["general"]["PASSWORD"]
        database = st.secrets["general"]["DATABASE"]
        
        logger.info(f"Configurações carregadas - Host: {host}, Database: {database}, User: {user}")
        
        # Tentar resolver o hostname
        try:
            ip = socket.gethostbyname(host)
            logger.info(f"Hostname {host} resolvido para IP: {ip}")
        except socket.gaierror as e:
            logger.error(f"Erro ao resolver hostname {host}: {e}")
            raise

        config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": 3306,
            "connect_timeout": 10,
            "cursorclass": pymysql.cursors.DictCursor  # Usar DictCursor para retornar dicionários
        }

        logger.info("Iniciando conexão MySQL...")
        conn = pymysql.connect(**config)
        
        if conn.open:
            db_info = conn.get_server_info()
            logger.info(f"Conexão estabelecida com sucesso! Versão MySQL: {db_info}")
            
            # Testar execução de query simples
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            logger.info("Teste de query executado com sucesso")
            return conn
        else:
            raise pymysql.Error("Conexão não estabelecida")

    except pymysql.Error as e:
        error_code = getattr(e, 'args', [0])[0]  # pymysql retorna o código de erro no primeiro argumento
        logger.error(f"Erro MySQL ({error_code}): {str(e)}")
        
        if error_code == 2003:
            msg = "Não foi possível conectar ao servidor MySQL"
        elif error_code == 1045:
            msg = "Acesso negado - usuário/senha incorretos"
        elif error_code == 1049:
            msg = "Banco de dados não existe"
        else:
            msg = f"Erro MySQL: {str(e)}"
        
        st.error(msg)
        return None

    except Exception as e:
        logger.error(f"Erro inesperado na conexão: {str(e)}")
        logger.exception("Stacktrace completo:")
        st.error(f"Erro na conexão com o banco: {str(e)}")
        return None