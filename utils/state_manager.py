import streamlit as st

class StateManager:

    @staticmethod
    def get_state(key, default=None):
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_state(key, value):
        st.session_state[key] = value

    @staticmethod
    def clear_state(keys):
        for key in keys:
            st.session_state.pop(key, None)
    