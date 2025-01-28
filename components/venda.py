# components/carros/view.py
from utils.state_manager import StateManager
from utils.templates import render_dashboard
import streamlit as st

def venda():
    if StateManager.get_state('logado'):
        render_dashboard(
            title="Dashboard - Vendedor",
            power_bi_url="https://app.powerbi.com/view?r=eyJrIjoiMjVmNmI0YTMtZjFmNC00YTMyLWIzMGEtMTVkMzYyNzM4ZDQ2IiwidCI6ImMxOTIyMjIwLTgwMjYtNGNhNi04MmU0LWY5MDI0M2YxNTI0MiJ9"
        )
    else:
        StateManager.set_state('selected_page', 'Login')
        st.rerun()
