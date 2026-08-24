"""
FinMate AI - Reports Page
===========================
Generate and export financial reports in CSV and TXT formats.
"""

from __future__ import annotations

import datetime
import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from utils.export import (
    export_expenses_csv,
    export_budget_csv,
    export_goals_csv,
    export_summary_txt,
    report_filename,
)
from backend.adapter import (
    get_all_expenses,
    get_spending_summary,
    calculate_budget,
    get_goals,
)


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>📄 Reports</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Generate and export your financial reports.</p>",
        unsafe_allow_html=True,
    )

    # ── Fetch all data once ────────────────────────────────────────
    expenses    = get_all_expenses()
    summary     = get_spending_summary()
    budget_data = calculate_budget()
    goals       = get_goals()
    advice      = st.session_state.get("last_advice")

    if not expenses:
        st.info("No expense data yet. Add some expenses to generate reports.")
        return

    # ── Report summary ─────────────────────────────────────────────
    st.markdown("### Report Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_mini_kpi("Total Spending",   f"₹{summary.get('total_spending', 0):,.0f}",   "💸"), unsafe_allow_html=True)
    with c2:
        st.markdown(_mini_kpi("Transactions",     str(summary.get('transaction_count', 0)),      "🔢"), unsafe_allow_html=True)
    with c3:
        st.markdown(_mini_kpi("Categories",       str(len(summary.get('by_category', {}))),      "🏷️"), unsafe_allow_html=True)
    with c4:
        st.markdown(_mini_kpi("Active Goals",     str(len(goals)),                               "🎯"), unsafe_allow_html=True)

    st.markdown("<hr class='fm-divider'>", unsafe_allow_html=True)

    # ── Download buttons ───────────────────────────────────────────
    st.markdown("### Export Reports")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "All reports are generated from your current data at the time of download.</p>",
        unsafe_allow_html=True,
    )

    row1_l, row1_r = st.columns(2)
    row2_l, row2_r = st.columns(2)

    # 1. Expense CSV
    with row1_l:
        with st.container():
            st.markdown(
                _report_card(
                    "📋 Expense List",
                    "Full transaction history with date, merchant, category, amount, and source.",
                    "CSV",
                ),
                unsafe_allow_html=True,
            )
            csv_data = export_expenses_csv(expenses)
            st.download_button(
                "⬇️  Download Expense CSV",
                data=csv_data,
                file_name=report_filename("expenses", "csv"),
                mime="text/csv",
                use_container_width=True,
            )

    # 2. Budget CSV
    with row1_r:
        with st.container():
            st.markdown(
                _report_card(
                    "💰 Budget Report",
                    "Category-wise budget vs actual spending with status and remaining amounts.",
                    "CSV",
                ),
                unsafe_allow_html=True,
            )
            budget_csv = export_budget_csv(budget_data)
            st.download_button(
                "⬇️  Download Budget CSV",
                data=budget_csv,
                file_name=report_filename("budget", "csv"),
                mime="text/csv",
                use_container_width=True,
            )

    # 3. Goals CSV
    with row2_l:
        with st.container():
            st.markdown(
                _report_card(
                    "🎯 Goals Report",
                    "All savings goals with target, current amount, progress %, and deadlines.",
                    "CSV",
                ),
                unsafe_allow_html=True,
            )
            goals_csv = export_goals_csv(goals)
            st.download_button(
                "⬇️  Download Goals CSV",
                data=goals_csv,
                file_name=report_filename("goals", "csv"),
                mime="text/csv",
                use_container_width=True,
            )

    # 4. Full Text Summary
    with row2_r:
        with st.container():
            st.markdown(
                _report_card(
                    "📝 Full Summary Report",
                    "Complete financial summary including spending, budget, goals, "
                    "and AI advice (if generated).",
                    "TXT",
                ),
                unsafe_allow_html=True,
            )
            txt_data = export_summary_txt(expenses, summary, budget_data, goals, advice)
            st.download_button(
                "⬇️  Download Full Report (TXT)",
                data=txt_data,
                file_name=report_filename("summary", "txt"),
                mime="text/plain",
                use_container_width=True,
            )

    st.markdown("<hr class='fm-divider'>", unsafe_allow_html=True)

    # ── On-screen preview tabs ─────────────────────────────────────
    st.markdown("### Preview Reports")
    tab_exp, tab_budget, tab_goals, tab_txt = st.tabs([
        "📋 Expenses", "💰 Budget", "🎯 Goals", "📝 Full Summary"
    ])

    with tab_exp:
        _preview_expenses(expenses, summary)

    with tab_budget:
        _preview_budget(budget_data)

    with tab_goals:
        _preview_goals(goals)

    with tab_txt:
        txt_preview = txt_data.decode("utf-8")
        st.code(txt_preview, language="text")

    # ── Privacy notice ─────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            margin-top:1.5rem;
            padding:0.8rem 1rem;
            background:rgba(148,163,184,0.07);
            border:1px solid {COLORS['border']};
            border-radius:8px;
            font-size:0.75rem;
            color:{COLORS['text_muted']};
        ">
            🔒 <strong>Privacy Notice:</strong> All data is stored locally on your device.
            FinMate AI does not transmit your financial data to any external servers.
            Exported files are for your personal use only.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Preview helpers
# ---------------------------------------------------------------------------

def _preview_expenses(expenses: list[dict], summary: dict) -> None:
    st.markdown(
        f"**{len(expenses)} transactions** &nbsp;·&nbsp; "
        f"Total: **₹{summary.get('total_spending', 0):,.2f}**"
    )
    df = pd.DataFrame([{
        "Date":         e.get("date", ""),
        "Merchant":     e.get("merchant", ""),
        "Category":     e.get("category", ""),
        "Amount (₹)":   e.get("amount", 0),
        "Payment":      e.get("payment", ""),
        "Source":       e.get("source", ""),
    } for e in sorted(expenses, key=lambda x: str(x.get("date", "")), reverse=True)])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={"Amount (₹)": st.column_config.NumberColumn(format="₹%.2f")},
    )


def _preview_budget(budget_data: dict) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Income",         f"₹{budget_data.get('income', 0):,.0f}")
    c2.metric("Total Spent",    f"₹{budget_data.get('total_spent', 0):,.0f}")
    c3.metric("Savings Est.",   f"₹{budget_data.get('savings_estimate', 0):,.0f}")

    rows = [{
        "Category":        r["category"],
        "Budget (₹)":      r["budget"],
        "Spent (₹)":       r["spent"],
        "Remaining (₹)":   r["remaining"],
        "Usage %":         r["pct"],
        "Status":          "⚠️ Over" if r["over_budget"] else "✅ OK",
    } for r in budget_data.get("by_category", []) if r["budget"] > 0]

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Budget (₹)":    st.column_config.NumberColumn(format="₹%.0f"),
                "Spent (₹)":     st.column_config.NumberColumn(format="₹%.0f"),
                "Remaining (₹)": st.column_config.NumberColumn(format="₹%.0f"),
                "Usage %":       st.column_config.NumberColumn(format="%.1f%%"),
            },
        )


def _preview_goals(goals: list[dict]) -> None:
    if not goals:
        st.info("No goals recorded.")
        return

    rows = [{
        "Goal":          g.get("name", ""),
        "Target (₹)":   g.get("target", 0),
        "Current (₹)":  g.get("current", 0),
        "Progress %":   round(g.get("current", 0) / g.get("target", 1) * 100, 1) if g.get("target") else 0,
        "Deadline":     g.get("deadline", ""),
    } for g in goals]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Target (₹)":  st.column_config.NumberColumn(format="₹%.0f"),
            "Current (₹)": st.column_config.NumberColumn(format="₹%.0f"),
            "Progress %":  st.column_config.NumberColumn(format="%.1f%%"),
        },
    )


# ---------------------------------------------------------------------------
# Card HTML helpers
# ---------------------------------------------------------------------------

def _report_card(title: str, description: str, file_type: str) -> str:
    type_color = COLORS["accent_teal"] if file_type == "CSV" else COLORS["accent_blue"]
    return f"""
    <div class="fm-card" style="margin-bottom:0.5rem; min-height:90px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="font-weight:700; font-size:0.95rem;">{title}</div>
            <span style="
                background:{type_color}22; color:{type_color};
                font-size:0.68rem; font-weight:700; padding:2px 8px;
                border-radius:4px; letter-spacing:0.05em;">
                {file_type}
            </span>
        </div>
        <div style="font-size:0.8rem; color:{COLORS['text_muted']};
                    margin-top:4px; line-height:1.4;">
            {description}
        </div>
    </div>
    """


def _mini_kpi(label: str, value: str, icon: str) -> str:
    return f"""
    <div class="fm-metric-card">
        <div class="fm-metric-icon">{icon}</div>
        <div class="fm-metric-label">{label}</div>
        <div class="fm-metric-value" style="font-size:1.5rem;">{value}</div>
    </div>
    """
