# app.py

import streamlit as st
from code.utils.db import initialize_db, ensure_admin_exists, get_connection
from code.roles.admin import Admin
from code.roles.coordinator import Coordinator
from code.roles.local_manager import LocalManager

# ----------------------------------------
# 1. Initialize the application environment
# ----------------------------------------

# Ensure all database tables exist
initialize_db()

# Ensure at least one admin account is present (auto-creates if none)
ensure_admin_exists()

# Set page title
st.title("Medical Shift Planner — Role Test")

# ----------------------------------------
# 2. Simulate user role (placeholder for real login)
# ----------------------------------------

# This dropdown lets you manually simulate logging in as a specific role
# In production, this will be replaced with real authentication logic
role = st.selectbox("Simulate login as:", ["admin", "coordinator", "local_manager"])

# Simulated user ID for all roles
# In real app: you'd get this from session state after login
user_id = 1

# Create a database connection for passing to the role classes
conn = get_connection()

# ----------------------------------------
# 3. Instantiate the appropriate role class
#    and display test outputs from backend
# ----------------------------------------

# ADMIN: Test listing accounts
if role == "admin":
    admin = Admin(conn, user_id)
    st.subheader("Admin View: All User Accounts")
    accounts = admin.list_accounts()
    st.write(accounts)

# COORDINATOR: Test listing all workers
elif role == "coordinator":
    coordinator = Coordinator(conn, user_id)
    st.subheader("Coordinator View: All Workers")
    workers = coordinator.list_workers()
    st.write(workers)

# LOCAL MANAGER: Test listing shifts
elif role == "local_manager":
    manager = LocalManager(conn, user_id)
    st.subheader("Local Manager View: Available Shifts")
    shifts = manager.list_available_shifts()
    st.write(shifts)

# ----------------------------------------
# 4. Developer Tip: Add dummy data if needed
# ----------------------------------------

# This section can be uncommented to inject test data for manual testing
# You may need to pre-fill some data like locations, shifts, workers
# depending on what your queries depend on

cursor = conn.cursor()
cursor.execute("INSERT INTO locations (name, address) VALUES (?, ?)", ("General Hospital", "123 Main St"))
cursor.execute("INSERT INTO shifts (location_id, start_time, end_time) VALUES (?, ?, ?)", (1, '2025-05-06 08:00', '2025-05-06 12:00'))
conn.commit()
