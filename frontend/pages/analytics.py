"""
FinMate AI - Analytics Page
==============================
Detailed spending analytics with multiple chart types and category breakdowns.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from frontend.components.charts import (
    category_donut_chart,
    category_bar_chart,
    monthly_bar_chart,
    spending_trend_chart,
    daily_bar_chart,
)
from backend.adapter import get_spending_summary, get_all_expenses


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>📊 Analytics</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Deep-dive into your spending patterns.</p>",
        unsafe_allow_html=True,
    )

    summary  = get_spending_summary()
    expenses = get_all_expenses()

    if not expenses:
        st.info("No expense data yet. Add some expenses to see your analytics.")
        return

    by_cat        = summary.get("by_category", {})
    monthly_trend = summary.get("monthly_trend", [])
    daily_spend   = summary.get("daily_spending", [])

    # ── Category Analysis ─────────────────────────────────────────
    st.markdown("### Category Analysis")

    # Category metric tiles
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    if sorted_cats:
        cols = st.columns(min(len(sorted_cats), 4))
        for idx, (cat, amt) in enumerate(sorted_cats[:4]):
            total = summary.get("total_spending", 1) or 1
            pct   = amt / total * 100
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class="fm-metric-card">
                        <div class="fm-metric-label">{cat}</div>
                        <div class="fm-metric-value" style="font-size:1.35rem;">
                            ₹{amt:,.0f}
                        </div>
                        <div class="fm-metric-delta">{pct:.1f}% of total</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if len(sorted_cats) > 4:
        st.markdown("<br>", unsafe_allow_html=True)
        cols2 = st.columns(min(len(sorted_cats) - 4, 4))
        for idx, (cat, amt) in enumerate(sorted_cats[4:8]):
            total = summary.get("total_spending", 1) or 1
            pct   = amt / total * 100
            with cols2[idx % 4]:
                st.markdown(
                    f"""
                    <div class="fm-metric-card">
                        <div class="fm-metric-label">{cat}</div>
                        <div class="fm-metric-value" style="font-size:1.35rem;">
                            ₹{amt:,.0f}
                        </div>
                        <div class="fm-metric-delta">{pct:.1f}% of total</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row 1 ──────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            category_donut_chart(by_cat),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with col2:
        st.plotly_chart(
            category_bar_chart(by_cat),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Spending Trends ───────────────────────────────────────────
    st.markdown("### Spending Trends")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            monthly_bar_chart(monthly_trend),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with col4:
        st.plotly_chart(
            daily_bar_chart(daily_spend),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # Full trend line
    st.plotly_chart(
        spending_trend_chart(daily_spend),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # ── Category Deep-Dive Table ───────────────────────────────────
    st.markdown("### Detailed Category Breakdown")
    total_spending = summary.get("total_spending", 0)

    rows = []
    for cat, amt in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
        cat_expenses = [e for e in expenses if e.get("category") == cat]
        avg = amt / len(cat_expenses) if cat_expenses else 0
        pct = amt / total_spending * 100 if total_spending else 0
        rows.append({
            "Category":      cat,
            "Transactions":  len(cat_expenses),
            "Total (₹)":     round(amt, 2),
            "Avg per Txn (₹)": round(avg, 2),
            "% of Total":    round(pct, 1),
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total (₹)":       st.column_config.NumberColumn(format="₹%.2f"),
                "Avg per Txn (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "% of Total":      st.column_config.NumberColumn(format="%.1f%%"),
            },
        )

    # ── Payment Method Breakdown ───────────────────────────────────
    st.markdown("### Payment Method Breakdown")
    pay_counts: dict[str, dict] = {}
    for e in expenses:
        pm = e.get("payment", "Unknown")
        if pm not in pay_counts:
            pay_counts[pm] = {"count": 0, "total": 0}
        pay_counts[pm]["count"] += 1
        pay_counts[pm]["total"] += e.get("amount", 0)

    pay_rows = [
        {
            "Payment Method": pm,
            "Transactions":   v["count"],
            "Total Spent (₹)": round(v["total"], 2),
            "Avg Amount (₹)": round(v["total"] / v["count"], 2),
        }
        for pm, v in sorted(pay_counts.items(), key=lambda x: x[1]["total"], reverse=True)
    ]
    if pay_rows:
        st.dataframe(
            pd.DataFrame(pay_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total Spent (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Avg Amount (₹)":  st.column_config.NumberColumn(format="₹%.2f"),
            },
        )
