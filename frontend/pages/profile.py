"""
FinMate AI - Profile Page
===========================
Shows user account details and allows password change.
"""

from __future__ import annotations

import streamlit as st
from frontend.styles import COLORS


def render() -> None:
    username = st.session_state.get("username", "User")
    email    = st.session_state.get("email", "")
    user_id  = st.session_state.get("user_id", "—")

    st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Your account details and security settings.</p>",
        unsafe_allow_html=True,
    )

    # ── Profile card ──────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:{COLORS['bg_card']}; border:1px solid {COLORS['border']};
                    border-radius:14px; padding:2rem; margin-bottom:1.5rem;
                    display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap;">
            <div style="font-size:4rem; line-height:1; flex-shrink:0;">👤</div>
            <div>
                <div style="font-size:1.5rem; font-weight:800;
                            color:{COLORS['text_primary']};">{username}</div>
                <div style="font-size:0.88rem; color:{COLORS['text_muted']};
                            margin-top:4px;">{email}</div>
                <div style="margin-top:8px; display:flex; gap:10px; flex-wrap:wrap;">
                    <span style="background:{COLORS['accent_teal']}22;
                                 color:{COLORS['accent_teal']};
                                 border:1px solid {COLORS['accent_teal']}44;
                                 border-radius:20px; padding:3px 12px;
                                 font-size:0.75rem; font-weight:700;">
                        User ID &nbsp;#{user_id}
                    </span>
                    <span style="background:{COLORS['accent_blue']}22;
                                 color:{COLORS['accent_blue']};
                                 border:1px solid {COLORS['accent_blue']}44;
                                 border-radius:20px; padding:3px 12px;
                                 font-size:0.75rem; font-weight:700;">
                        ✓ Verified Account
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Info grid ──────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class="fm-metric-card">
                <div class="fm-metric-icon">🏷️</div>
                <div class="fm-metric-label">Username</div>
                <div class="fm-metric-value" style="font-size:1.1rem;">{username}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="fm-metric-card">
                <div class="fm-metric-icon">🆔</div>
                <div class="fm-metric-label">User ID</div>
                <div class="fm-metric-value" style="font-size:1.1rem;">#{user_id}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="fm-metric-card">
                <div class="fm-metric-icon">📧</div>
                <div class="fm-metric-label">Email</div>
                <div class="fm-metric-value" style="font-size:0.85rem;
                     word-break:break-all;">{email}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Change password ────────────────────────────────────────────
    st.markdown("### 🔒 Change Password")
    with st.form("change_password_form", clear_on_submit=True):
        old_pass  = st.text_input("Current Password", type="password",
                                  placeholder="Enter your current password")
        new_pass  = st.text_input("New Password", type="password",
                                  placeholder="At least 6 characters")
        conf_pass = st.text_input("Confirm New Password", type="password",
                                  placeholder="Repeat new password")
        submitted = st.form_submit_button("Update Password", use_container_width=True)

    if submitted:
        if not old_pass or not new_pass or not conf_pass:
            st.error("Please fill in all password fields.")
        elif new_pass != conf_pass:
            st.error("New passwords do not match.")
        elif len(new_pass) < 6:
            st.error("New password must be at least 6 characters.")
        else:
            from backend.auth import update_password
            result = update_password(user_id, old_pass, new_pass)
            if result["success"]:
                st.success(f"✅ {result['message']}")
            else:
                st.error(result["message"])

    st.divider()

    # ── Sign out ───────────────────────────────────────────────────
    st.markdown("### 🚪 Sign Out")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "You will be returned to the login screen.</p>",
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", type="secondary", use_container_width=False):
        for key in ["user_id", "username", "email", "selected_page"]:
            st.session_state.pop(key, None)
        st.rerun()
