# utils/templates.py
import streamlit as st

def render_dashboard(title: str, power_bi_url: str):
    """
    Renders a dashboard page with a given title and Power BI URL.
    """
    # Botão de voltar para o dashboard principal
    if st.button("Voltar à Página Inicial"):
        st.session_state['selected_page'] = "Dashboard"
        st.experimental_rerun()

    # Exibe o título do dashboard
    st.markdown(f"""
        <h1 style="text-align: center; font-size: 2.5em; color: #000000;">{title}</h1>
    """, unsafe_allow_html=True)

    # Exibe o iframe com o dashboard do Power BI
    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
            <iframe title="{title}" width="90%" height="800" 
                    src="{power_bi_url}" frameborder="0" allowFullScreen="true"
                    style="border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            </iframe>
        </div>
    """, unsafe_allow_html=True)
