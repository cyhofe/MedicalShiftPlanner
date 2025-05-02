import streamlit as st

st.title("Medical Shift Planner")
st.write("Welcome to the planner!")


# start and input the database
from code.utils.db import initialize_db

initialize_db()
