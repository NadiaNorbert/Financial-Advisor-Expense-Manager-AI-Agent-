"""
FinMate AI - Budget Page
==========================
Monthly income setup, per-category budget allocation, and spending progress bars.
"""

from __future__ import annotations

import streamlit as st

from frontend.styles import COLORS
from frontend.components.charts import budget_vs_spent_chart
from backend.adapter import (
    calculate_budget,
    get_budget_settings,
    save_budget_settings,
    CATEGORIES,
)


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>💰 Budget</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Set your monthly income and category budgets, then track progress in real time.</p>",
        unsafe_allow_html=True,
    )

    tab_overview, tab_settings = st.tabs(["📊  Budget Overview", "⚙️  Budget Settings"])

    with tab_overview:
        _budget_overview()

    with tab_settings:
        _budget_settings()


# ---------------------------------------------------------------------------
# Budget Overview
# ---------------------------------------------------------------------------

def _budget_overview() -> None:
    data = calculate_budget()

    income          = data.get("income", 0)
    total_budget    = data.get("total_budget", 0)
    total_spent     = data.get("total_spent", 0)
    remaining       = data.get("remaining", 0)
    savings_est     = data.get("savings_estimate", 0)
    by_category     = data.get("by_category", [])

    # ── Summary KPIs ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi("Monthly Income", f"₹{income:,.0f}", "💵"), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi("Total Budget", f"₹{total_budget:,.0f}", "📋"), unsafe_allow_html=True)
    with c3:
        color = COLORS["accent_red"] if remaining < 0 else COLORS["accent_green"]
        st.markdown(_kpi("Remaining", f"₹{remaining:,.0f}", "💰", color), unsafe_allow_html=True)
    with c4:
        color = COLORS["accent_green"] if savings_est > 0 else COLORS["accent_red"]
        st.markdown(_kpi("Savings Est.", f"₹{savings_est:,.0f}", "🎯", color), unsafe_allow_html=True)

    # ── Overall progress bar ──────────────────────────────────────
    if total_budget > 0:
        overall_pct = min(total_spent / total_budget * 100, 100)
        bar_color = (
            COLORS["accent_red"]    if overall_pct > 90 else
            COLORS["accent_orange"] if overall_pct > 70 else
            COLORS["accent_green"]
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="fm-card">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-weight:600;">Overall Budget Usage</span>
                    <span style="color:{bar_color}; font-weight:700;">
                        {overall_pct:.1f}%
                    </span>
                </div>
                <div class="fm-progress-wrap">
                    <div class="fm-progress-bar"
                         style="width:{overall_pct}%; background:{bar_color};"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;
                            font-size:0.75rem; color:{COLORS['text_muted']};">
                    <span>₹{total_spent:,.0f} spent</span>
                    <span>₹{total_budget:,.0f} budget</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Category progress bars ────────────────────────────────────
    st.markdown("### Category Progress")

    active_cats = [row for row in by_category if row.get("budget", 0) > 0]

    if not active_cats:
        st.info("No category budgets set yet. Go to **Budget Settings** to add them.")
    else:
        for row in active_cats:
            _category_progress_bar(row)

    # ── Budget vs Spent chart ─────────────────────────────────────
    if active_cats:
        st.markdown("### Budget vs Actual")
        st.plotly_chart(
            budget_vs_spent_chart(active_cats),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Categories with no budget ─────────────────────────────────
    unset_cats = [row for row in by_category if row.get("budget", 0) == 0 and row.get("spent", 0) > 0]
    if unset_cats:
        st.markdown("### Unbudgeted Spending")
        st.warning(
            "You have spending in categories without a budget. "
            "Consider setting limits in **Budget Settings**."
        )
        for row in unset_cats:
            st.markdown(
                f"""
                <div class="fm-expense-row" style="margin-bottom:0.4rem;">
                    <div>
                        <div class="fm-expense-merchant">{row['category']}</div>
                        <div class="fm-expense-meta">No budget set</div>
                    </div>
                    <div class="fm-expense-amount"
                         style="color:{COLORS['accent_orange']};">
                        ₹{row['spent']:,.0f} spent
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _category_progress_bar(row: dict) -> None:
    cat       = row["category"]
    budget    = row["budget"]
    spent     = row["spent"]
    pct       = row["pct"]
    over      = row["over_budget"]
    remaining = row["remaining"]

    bar_color = COLORS["accent_red"] if over else (
        COLORS["accent_orange"] if pct > 80 else COLORS["accent_green"]
    )
    bar_width = min(pct, 100)

    over_text = ""
    if over:
        over_text = (
            f'<span style="color:{COLORS["accent_red"]}; font-weight:700; font-size:0.78rem;">'
            f'⚠️ Over budget by ₹{abs(remaining):,.0f}</span>'
        )
    else:
        over_text = (
            f'<span style="color:{COLORS["text_muted"]}; font-size:0.78rem;">'
            f'₹{remaining:,.0f} remaining</span>'
        )

    st.markdown(
        f"""
        <div class="fm-card" style="padding:0.9rem 1.2rem; margin-bottom:0.6rem;">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:6px;">
                <span style="font-weight:600; font-size:0.95rem;">{cat}</span>
                <span style="font-size:0.85rem; color:{bar_color}; font-weight:700;">
                    {pct:.0f}%
                </span>
            </div>
            <div class="fm-progress-wrap">
                <div class="fm-progress-bar"
                     style="width:{bar_width}%; background:{bar_color};"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <span style="font-size:0.78rem; color:{COLORS['text_muted']};">
                    ₹{spent:,.0f} / ₹{budget:,.0f}
                </span>
                {over_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Budget Settings
# ---------------------------------------------------------------------------

def _budget_settings() -> None:
    st.markdown("#### Configure Your Budget")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Set your monthly take-home income and how much you want to allocate "
        "to each spending category. Leave a category at 0 to skip it.</p>",
        unsafe_allow_html=True,
    )

    settings = get_budget_settings()
    income   = settings.get("income", 30000)
    budgets  = settings.get("budgets", {})

    with st.form("budget_settings_form"):
        st.markdown("##### Monthly Income")
        new_income = st.number_input(
            "Take-home income (₹)",
            min_value=0.0,
            value=float(income),
            step=500.0,
            format="%.0f",
        )

        st.markdown("##### Category Budgets")
        st.caption("Set to 0 to leave a category untracked.")

        new_budgets: dict[str, float] = {}
        cols = st.columns(2)
        for idx, cat in enumerate(CATEGORIES):
            with cols[idx % 2]:
                default_val = float(budgets.get(cat, 0))
                new_budgets[cat] = st.number_input(
                    f"{cat} (₹)",
                    min_value=0.0,
                    value=default_val,
                    step=100.0,
                    format="%.0f",
                    key=f"budget_{cat}",
                )

        # Live summary
        total_allocated = sum(v for v in new_budgets.values() if v > 0)
        leftover        = new_income - total_allocated
        st.markdown(
            f"""
            <div class="fm-card" style="margin-top:1rem; padding:0.8rem 1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.88rem;">
                    <span>Monthly income:</span>
                    <strong>₹{new_income:,.0f}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.88rem;">
                    <span>Total allocated:</span>
                    <strong>₹{total_allocated:,.0f}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.88rem;
                            color:{'#10B981' if leftover >= 0 else '#EF4444'};">
                    <span>Unallocated / Savings:</span>
                    <strong>₹{leftover:,.0f}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button("💾  Save Budget Settings", use_container_width=True)

    if submitted:
        result = save_budget_settings(new_income, new_budgets)
        if result.get("success"):
            st.success("✅ Budget settings saved successfully!")
            st.rerun()
        else:
            st.error(f"Could not save settings: {result.get('message')}")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _kpi(label: str, value: str, icon: str, color: str = None) -> str:
    c = color or COLORS["accent_teal"]
    return f"""
    <div class="fm-metric-card">
        <div class="fm-metric-icon">{icon}</div>
        <div class="fm-metric-label">{label}</div>
        <div class="fm-metric-value" style="color:{c};">{value}</div>
    </div>
    """
