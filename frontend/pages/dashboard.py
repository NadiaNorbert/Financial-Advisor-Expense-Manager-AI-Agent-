"""
FinMate AI - Dashboard Page
=============================
Main landing page showing KPI metrics, recent transactions, and spending charts.
"""

import streamlit as st
import datetime
from frontend.components.metric_card import render_kpi_row
from frontend.components.expense_card import expense_card_list
from frontend.components.charts import (
    category_donut_chart,
    monthly_bar_chart,
    spending_trend_chart,
)
from frontend.styles import COLORS
from backend.adapter import get_spending_summary, get_all_expenses, get_budget_settings


def render() -> None:
    # ── Profile greeting bar ───────────────────────────────────────
    username = st.session_state.get("username", "User")
    email    = st.session_state.get("email", "")
    user_id  = st.session_state.get("user_id", "—")
    hour     = datetime.datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    col_greet, col_profile = st.columns([3, 1])
    with col_greet:
        st.markdown(
            f"""
            <div style="margin-bottom:1.5rem;">
                <h1 style="margin-bottom:2px;">🏠 Dashboard</h1>
                <p style="color:{COLORS['text_muted']}; font-size:0.9rem; margin:0;">
                    {greeting}, <strong style="color:{COLORS['accent_teal']};">{username}</strong>!
                    Here's your financial snapshot.
                    &nbsp;·&nbsp;
                    <span style="color:{COLORS['accent_teal']};">
                        {datetime.date.today().strftime('%A, %d %B %Y')}
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_profile:
        st.markdown(
            f"""
            <div style="background:{COLORS['bg_card']}; border:1px solid {COLORS['border']};
                        border-radius:12px; padding:0.75rem 1rem; text-align:center;
                        margin-bottom:1rem;">
                <div style="font-size:1.8rem; line-height:1;">👤</div>
                <div style="font-size:0.88rem; font-weight:700;
                            color:{COLORS['text_primary']}; margin-top:4px;">{username}</div>
                <div style="font-size:0.7rem; color:{COLORS['text_muted']};">
                    ID&nbsp;<code style="color:{COLORS['accent_teal']};">#{user_id}</code>
                </div>
                <div style="font-size:0.68rem; color:{COLORS['text_muted']};
                            margin-top:2px; word-break:break-all;">{email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⚙️ Profile", use_container_width=True, key="dash_profile_btn"):
            st.session_state.selected_page = "Profile"
            st.rerun()

    # ── Fetch data ─────────────────────────────────────────────────
    summary  = get_spending_summary()
    settings = get_budget_settings()
    expenses = get_all_expenses()

    income        = settings.get("income", 0)
    total_spent   = summary.get("total_spending", 0)
    monthly_spent = summary.get("monthly_spending", 0)
    total_budget  = sum(v for v in settings.get("budgets", {}).values() if v > 0)
    remaining     = total_budget - monthly_spent
    tx_count      = summary.get("transaction_count", 0)
    top_cat       = summary.get("top_category", "N/A")

    # ── KPI row ────────────────────────────────────────────────────
    render_kpi_row([
        {
            "label": "Total Spending",
            "value": f"₹{total_spent:,.0f}",
            "icon":  "💸",
            "delta": "All time",
        },
        {
            "label": "Monthly Spending",
            "value": f"₹{monthly_spent:,.0f}",
            "icon":  "📅",
            "delta": datetime.date.today().strftime("%B %Y"),
        },
        {
            "label": "Remaining Budget",
            "value": f"₹{remaining:,.0f}",
            "icon":  "💰",
            "delta": f"of ₹{total_budget:,.0f} budget",
            "accent_color": (
                COLORS["accent_red"]   if remaining < 0 else
                COLORS["accent_orange"] if remaining < total_budget * 0.2 else
                COLORS["accent_green"]
            ),
        },
        {
            "label": "Transactions",
            "value": str(tx_count),
            "icon":  "🔢",
            "delta": "total recorded",
        },
        {
            "label": "Top Category",
            "value": top_cat if top_cat != "N/A" else "N/A",
            "icon":  "🏆",
            "delta": "highest spending",
            "accent_color": COLORS["accent_orange"],
            "small_text": True,
        },
    ])

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Budget health bar ──────────────────────────────────────────
    if total_budget > 0:
        pct = min(monthly_spent / total_budget * 100, 100)
        bar_color = (
            COLORS["accent_red"]    if pct > 90 else
            COLORS["accent_orange"] if pct > 70 else
            COLORS["accent_green"]
        )
        status_text = (
            "🚨 Over budget!" if monthly_spent > total_budget else
            "⚠️ Almost at limit" if pct > 80 else
            "✅ On track"
        )
        st.markdown(
            f"""
            <div class="fm-card" style="margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between;
                            align-items:center; margin-bottom:8px;">
                    <span style="font-weight:600; font-size:0.9rem;">
                        Monthly Budget Health
                    </span>
                    <span style="font-size:0.85rem; color:{bar_color}; font-weight:600;">
                        {status_text} &nbsp; {pct:.1f}% used
                    </span>
                </div>
                <div class="fm-progress-wrap">
                    <div class="fm-progress-bar"
                         style="width:{pct}%; background:{bar_color};"></div>
                </div>
                <div style="display:flex; justify-content:space-between;
                            margin-top:4px; font-size:0.75rem;
                            color:{COLORS['text_muted']};">
                    <span>₹{monthly_spent:,.0f} spent</span>
                    <span>₹{total_budget:,.0f} budget</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Charts row ─────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1.4])

    with col_left:
        by_cat = summary.get("by_category", {})
        st.plotly_chart(
            category_donut_chart(by_cat),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_right:
        monthly_trend = summary.get("monthly_trend", [])
        if len(monthly_trend) >= 2:
            st.plotly_chart(
                monthly_bar_chart(monthly_trend),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.markdown(
                f"""
                <div style="border:1px solid {COLORS['border']}; border-radius:12px;
                            padding:2rem; text-align:center; color:{COLORS['text_muted']};">
                    <div style="font-size:1.8rem; margin-bottom:0.5rem;">📅</div>
                    <div style="font-weight:600; color:{COLORS['text_primary']};">Monthly Spending</div>
                    <div style="font-size:0.82rem; margin-top:0.3rem;">
                        Add expenses across multiple months to see the trend.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Spending trend ─────────────────────────────────────────────
    daily = summary.get("daily_spending", [])
    if len(daily) >= 2:
        st.plotly_chart(
            spending_trend_chart(daily),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Recent transactions ────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between;
                    align-items:center; margin:1rem 0 0.5rem 0;">
            <h2 style="margin:0;">Recent Transactions</h2>
            <span style="font-size:0.8rem; color:{COLORS['text_muted']};">
                Showing last 8
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sorted_expenses = sorted(expenses, key=lambda x: str(x.get("date", "")), reverse=True)
    expense_card_list(sorted_expenses, limit=8)

    if len(expenses) > 8:
        st.info(
            f"Showing 8 of {len(expenses)} transactions. "
            "Go to **💳 Expenses** to see all."
        )

    # ── Quick actions ──────────────────────────────────────────────
    st.markdown("<hr class='fm-divider'>", unsafe_allow_html=True)
    st.markdown("#### Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("📸  Upload Receipt",  use_container_width=True):
            st.session_state.selected_page = "Upload Expense"
            st.rerun()
    with qa2:
        if st.button("✍️  Add Manually",    use_container_width=True):
            st.session_state.selected_page = "Expenses"
            st.rerun()
    with qa3:
        if st.button("💡  Get AI Advice",   use_container_width=True):
            st.session_state.selected_page = "AI Advisor"
            st.rerun()
    with qa4:
        if st.button("📄  View Reports",    use_container_width=True):
            st.session_state.selected_page = "Reports"
            st.rerun()


