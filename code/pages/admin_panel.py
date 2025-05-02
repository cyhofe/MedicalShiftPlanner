# pages/admin_panel.py

import streamlit as st
from code.utils.db import authenticate_account, get_connection
from code.roles.admin import Admin

st.title("Admin Panel")

# -------------------------------
# Session Initialization
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.role = None

# -------------------------------
# Login Form
# -------------------------------
if not st.session_state.authenticated:
    st.subheader("Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        user = authenticate_account(username, password)
        if user and user["role"] == "admin":
            st.session_state.authenticated = True
            st.session_state.user_id = user["id"]
            st.session_state.role = user["role"]
            st.experimental_rerun()
        else:
            st.error("Invalid credentials or not an admin.")

# -------------------------------
# Admin Panel: Show After Login
# -------------------------------
if st.session_state.authenticated and st.session_state.role == "admin":
    st.success("Welcome, Admin!")
    conn = get_connection()
    admin = Admin(conn, st.session_state.user_id)

    # List accounts
    st.subheader("User Accounts")
    accounts = admin.list_accounts()
    for acc in accounts:
        st.text(f"{acc[1]} ({acc[4]}) - {acc[2]}")

    # Add new user form
    st.subheader("Add New User")
    new_name = st.text_input("New Name")
    new_username = st.text_input("New Username")
    new_email = st.text_input("New Email")
    new_password = st.text_input("New Password", type="password")
    new_role = st.selectbox("Role", ["coordinator", "local_manager"])

    if st.button("Create User"):
        try:
            admin.add_account(new_name, new_username, new_email, new_password, new_role)
            st.success("User created successfully.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")

