# components/carros/view.py
from utils.state_manager import StateManager
from utils.templates import render_dashboard
import streamlit as st

def gsv():
    if StateManager.get_state('logado'):
       render_dashboard(
            title="Dashboard - GSV",
            power_bi_url="https://app.powerbi.com/view?r=eyJrIjoiODZmYzk4MGMtMmYzMi00ZWViLWE2OWItYjg4NTVmNzIwMzg2IiwidCI6ImMxOTIyMjIwLTgwMjYtNGNhNi04MmU0LWY5MDI0M2YxNTI0MiJ9"
        )
    else:
        StateManager.set_state('selected_page', 'Login')
        st.rerun()
