"""
FinMate AI - Authentication Page
==================================
Login and registration UI. Renders instead of the main app when
the user is not logged in.
"""

from __future__ import annotations

import streamlit as st
from frontend.styles import COLORS


def render_auth() -> bool:
    """Render the login/register page.

    Returns True if the user is now authenticated, False otherwise.
    """
    # Already logged in — nothing to do
    if st.session_state.get("user_id"):
        return True

    st.markdown(
        f"""
        <div style="max-width:420px; margin:4rem auto 0 auto; text-align:center;">
            <div style="font-size:3rem; margin-bottom:0.4rem;">💎</div>
            <div style="font-size:1.8rem; font-weight:800;
                        color:{COLORS['accent_teal']}; margin-bottom:4px;">
                FinMate AI
            </div>
            <div style="font-size:0.85rem; color:{COLORS['text_muted']};
                        margin-bottom:2rem; letter-spacing:0.04em;">
                Your AI-Powered Personal Finance Assistant
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centre the form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Create Account"])

        with tab_login:
            _login_form()

        with tab_register:
            _register_form()

    return bool(st.session_state.get("user_id"))


def _login_form() -> None:
    with st.form("login_form", clear_on_submit=False):
        st.markdown(
            f"<div style='font-size:0.82rem; color:{COLORS['text_muted']};"
            "margin-bottom:0.8rem;'>Sign in to your account</div>",
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", placeholder="your_username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        from backend.auth import login_user
        if not username or not password:
            st.error("Please fill in both fields.")
            return
        result = login_user(username, password)
        if result["success"]:
            st.session_state.user_id   = result["user_id"]
            st.session_state.username  = result["username"]
            st.session_state.email     = result["email"]
            st.session_state.selected_page = "Dashboard"
            st.success(result["message"])
            st.rerun()
        else:
            st.error(result["message"])


def _register_form() -> None:
    with st.form("register_form", clear_on_submit=True):
        st.markdown(
            f"<div style='font-size:0.82rem; color:{COLORS['text_muted']};"
            "margin-bottom:0.8rem;'>Create a free account</div>",
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", placeholder="choose_a_username", key="reg_user")
        email    = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        password = st.text_input("Password", type="password",
                                 placeholder="at least 6 characters", key="reg_pass")
        confirm  = st.text_input("Confirm Password", type="password",
                                 placeholder="repeat password", key="reg_confirm")
        submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        from backend.auth import register_user, login_user
        if password != confirm:
            st.error("Passwords do not match.")
            return
        result = register_user(username, email, password)
        if result["success"]:
            # Auto-login after registration
            login_result = login_user(username, password)
            if login_result["success"]:
                st.session_state.user_id   = login_result["user_id"]
                st.session_state.username  = login_result["username"]
                st.session_state.email     = login_result["email"]
                st.session_state.selected_page = "Dashboard"
                st.success(f"🎉 Account created! Welcome, {username}!")
                st.rerun()
        else:
            st.error(result["message"])
