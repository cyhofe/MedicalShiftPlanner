# medical_shift_planner/ui/sidebar.py
import streamlit as st

def render_sidebar():
    st.sidebar.header("Navigation")
    return st.sidebar.radio("Go to:", ["Home", "Schedule", "Settings"])
