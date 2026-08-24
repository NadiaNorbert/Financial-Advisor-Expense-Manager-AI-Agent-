"""
FinMate AI — Main Application Entry Point
==========================================
Run with:  streamlit run app.py
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────
st.set_page_config(
    page_title="FinMate AI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":    None,
        "Report a Bug": None,
        "About": (
            "**FinMate AI** — Your AI-Powered Personal Finance Assistant\n\n"
            "Track A · College Project · Built with Streamlit"
        ),
    },
)

# ── Load .env ─────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Apply global styles ───────────────────────────────────────────────────
from frontend.styles import apply_styles
apply_styles()

# ── Auth gate ─────────────────────────────────────────────────────────────
from frontend.pages.auth import render_auth
if not render_auth():
    st.stop()   # not logged in — show only the auth page

# ── Sidebar navigation ────────────────────────────────────────────────────
from frontend.components.sidebar import render_sidebar, render_topnav
page = render_sidebar()

# ── Top navigation bar (always visible, even when sidebar is collapsed) ───
render_topnav()

# ── Page routing ──────────────────────────────────────────────────────────
if page == "Dashboard":
    from frontend.pages.dashboard import render
    render()

elif page == "Upload Expense":
    from frontend.pages.upload_expense import render
    render()

elif page == "Expenses":
    from frontend.pages.expenses import render
    render()

elif page == "Analytics":
    from frontend.pages.analytics import render
    render()

elif page == "AI Advisor":
    from frontend.pages.advisor import render
    render()

elif page == "Budget":
    from frontend.pages.budget import render
    render()

elif page == "Goals":
    from frontend.pages.goals import render
    render()

elif page == "Splitwise":
    from frontend.pages.splitwise import render
    render()

elif page == "Reports":
    from frontend.pages.reports import render
    render()

elif page == "Profile":
    from frontend.pages.profile import render
    render()

else:
    st.error(f"Unknown page: {page}")
