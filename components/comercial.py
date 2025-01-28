# components/carros/view.py
from utils.state_manager import StateManager
from utils.templates import render_dashboard
import streamlit as st

def comercial():
    if StateManager.get_state('logado'):
        render_dashboard(
            title="Dashboard - Comercial",
            power_bi_url="https://app.powerbi.com/view?r=eyJrIjoiYWNjZmMzNDYtMTBlZi00NzBhLWJjYzYtYzg3NWNkZGEzYTE0IiwidCI6ImMxOTIyMjIwLTgwMjYtNGNhNi04MmU0LWY5MDI0M2YxNTI0MiJ9"
        )
    else:
        StateManager.set_state('selected_page', 'Login')
        st.rerun()
