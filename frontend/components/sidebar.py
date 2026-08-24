"""
FinMate AI - Sidebar Navigation
================================
Renders the left sidebar with the app logo, nav menu, and status indicators.
Returns the selected page name.
"""

import streamlit as st
from frontend.styles import COLORS


# Page definitions: (display label, internal key)
PAGES = [
    ("🏠  Dashboard",          "Dashboard"),
    ("📸  Upload Expense",     "Upload Expense"),
    ("💳  Expenses",           "Expenses"),
    ("📊  Analytics",          "Analytics"),
    ("💡  AI Advisor",         "AI Advisor"),
    ("💰  Budget",             "Budget"),
    ("🎯  Goals",              "Goals"),
    ("🤝  Splitwise",          "Splitwise"),
    ("📄  Reports",            "Reports"),
    ("👤  Profile",            "Profile"),
]

# Short labels for the compact top navbar
_NAV_SHORT = [
    ("🏠", "Dashboard"),
    ("📸", "Upload Expense"),
    ("💳", "Expenses"),
    ("📊", "Analytics"),
    ("💡", "AI Advisor"),
    ("💰", "Budget"),
    ("🎯", "Goals"),
    ("🤝", "Splitwise"),
    ("📄", "Reports"),
    ("👤", "Profile"),
]


def render_sidebar() -> str:
    """
    Renders the sidebar and returns the currently selected page key.
    """
    with st.sidebar:
        # ── Logo / brand ──────────────────────────────────────────
        st.markdown(
            f"""
            <div style="padding: 1rem 0 1.4rem 0; text-align: center;">
                <div style="font-size:2.4rem; line-height:1;">💎</div>
                <div style="font-size:1.45rem; font-weight:800;
                            color:{COLORS['accent_teal']}; margin-top:4px;">
                    FinMate AI
                </div>
                <div style="font-size:0.72rem; color:{COLORS['text_muted']};
                            margin-top:2px; letter-spacing:0.05em;">
                    Your AI-Powered Finance Assistant
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Navigation ────────────────────────────────────────────
        # Initialise selected page in session state
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Dashboard"

        for label, key in PAGES:
            is_active = st.session_state.selected_page == key
            btn_style = (
                f"background:linear-gradient(90deg, {COLORS['accent_teal']}22, transparent);"
                f"border-left:3px solid {COLORS['accent_teal']};"
                f"color:{COLORS['accent_teal']}; font-weight:700;"
            ) if is_active else (
                f"background:transparent; border-left:3px solid transparent;"
                f"color:{COLORS['text_primary']}; font-weight:500;"
            )

            # Render as a styled button
            if st.sidebar.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
            ):
                st.session_state.selected_page = key
                st.rerun()

        st.divider()

        # ── User info + logout ────────────────────────────────────
        username = st.session_state.get("username", "")
        if username:
            st.markdown(
                f"""
                <div style="padding:0.5rem 0; text-align:center;">
                    <div style="font-size:1.5rem;">👤</div>
                    <div style="font-size:0.85rem; font-weight:700;
                                color:{COLORS['text_primary']};">{username}</div>
                    <div style="font-size:0.7rem; color:{COLORS['text_muted']};">
                        {st.session_state.get('email', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.sidebar.button("🚪  Sign Out", use_container_width=True):
                for key in ["user_id", "username", "email", "selected_page"]:
                    st.session_state.pop(key, None)
                st.rerun()

        st.divider()

        # ── Status indicators ─────────────────────────────────────
        _render_status_panel()

        # ── Bottom footer ─────────────────────────────────────────
        st.markdown(
            f"""
            <div style="position:relative; margin-top:2rem;
                        font-size:0.7rem; color:{COLORS['text_muted']};
                        text-align:center; padding-bottom:0.5rem;">
                FinMate AI &nbsp;·&nbsp; v1.0.0<br/>
                <span style="font-size:0.65rem;">College Project — Track A</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.selected_page


def _render_status_panel() -> None:
    """Shows small status pills for backend / API availability."""
    from backend.adapter import is_backend_available

    def _pill(label: str, ok: bool) -> str:
        color = COLORS["accent_green"] if ok else COLORS["accent_orange"]
        icon = "●" if ok else "○"
        return (
            f'<span style="color:{color}; font-size:0.75rem; '
            f'font-weight:600;">{icon} {label}</span>'
        )

    ocr_ok  = is_backend_available("backend.ocr.expense_ocr")
    ai_ok   = is_backend_available("backend.advisor.advisor")
    db_ok   = is_backend_available("backend.expenses.crud")

    st.markdown(
        f"""
        <div style="font-size:0.68rem; color:{COLORS['text_muted']};
                    text-transform:uppercase; letter-spacing:0.08em;
                    margin-bottom:6px;">System Status</div>
        <div style="display:flex; flex-direction:column; gap:4px;">
            {_pill("OCR Engine",   ocr_ok)}
            {_pill("AI Advisor",   ai_ok)}
            {_pill("Database",     db_ok)}
            {_pill("Mock Mode", not (ocr_ok and ai_ok and db_ok))}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topnav() -> None:
    """Renders a compact horizontal navigation bar in the main content area.

    Always visible even when the sidebar is collapsed. Each icon button
    switches the active page via session state.
    """
    current = st.session_state.get("selected_page", "Dashboard")

    # Build one Streamlit button per page in a single row
    cols = st.columns(len(_NAV_SHORT))
    for col, (icon, key) in zip(cols, _NAV_SHORT):
        is_active = current == key
        # Use primary type for active page so it stands out
        with col:
            if st.button(
                icon,
                key=f"topnav_{key}",
                help=key,
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.selected_page = key
                st.rerun()
