import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

st.set_page_config(page_title=os.getenv("APP_TITLE", "Planner"))
st.title(os.getenv("APP_TITLE"))

st.write("Database is at:", os.getenv("DATABASE_URL"))
