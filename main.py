import streamlit as st

from medical_shift_planner.config import PAGE_TITLE, LAYOUT, SIDEBAR_STATE
from medical_shift_planner.ui.sidebar import render_sidebar
from medical_shift_planner.ui.pages.home import render_home
from medical_shift_planner.ui.pages.schedule import render_schedule
from medical_shift_planner.ui.pages.settings import render_settings


def main():
    """
    Streamlit entrypoint for Medical Shift Planner.
    Sets up page configuration, sidebar navigation, and routes to pages.
    """
    # Configure basic page settings
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE
    )

    # Render sidebar and capture selected page
    page = render_sidebar()

    # Route to the selected page
    if page == "Home":
        render_home()
    elif page == "Schedule":
        render_schedule()
    elif page == "Settings":
        render_settings()
    else:
        st.error(f"Unknown page: {page}")


if __name__ == "__main__":
    main()
