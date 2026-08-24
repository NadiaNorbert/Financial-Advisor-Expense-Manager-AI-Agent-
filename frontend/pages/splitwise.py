"""
FinMate AI - Splitwise Page
=============================
Display shared expenses from Splitwise with mock/demo fallback.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from backend.adapter import get_splitwise_expenses, is_backend_available, add_expense


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>🤝 Splitwise Expenses</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "View and import shared expenses from Splitwise.</p>",
        unsafe_allow_html=True,
    )

    # ── Status banner ──────────────────────────────────────────────
    splitwise_live = is_backend_available("backend.splitwise.splitwise_client")
    if not splitwise_live:
        st.markdown(
            f"""
            <div style="
                border: 2px dashed {COLORS['border']};
                border-radius: 14px;
                padding: 3rem 2rem;
                text-align: center;
                color: {COLORS['text_muted']};
                margin-top: 1.5rem;
            ">
                <div style="font-size:3rem; margin-bottom:0.75rem;">🔗</div>
                <div style="font-size:1.1rem; font-weight:700;
                            color:{COLORS['text_primary']}; margin-bottom:0.5rem;">
                    Splitwise Not Connected
                </div>
                <div style="font-size:0.88rem; max-width:420px; margin:0 auto;">
                    Connect your Splitwise account to view and import shared expenses here.
                    Add your Splitwise API credentials to <code>.env</code> to get started.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    else:
        st.success("✅ Splitwise connected — showing live data.")

    # ── Fetch ──────────────────────────────────────────────────────
    try:
        expenses = get_splitwise_expenses()
    except Exception as e:
        st.error(f"Could not load Splitwise data: {e}")
        return

    if not expenses:
        st.info("No Splitwise expenses found.")
        return

    # ── Summary ────────────────────────────────────────────────────
    total_share   = sum(e.get("user_share", 0) for e in expenses)
    total_expense = sum(e.get("total", 0) for e in expenses)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">🧾</div>'
            f'<div class="fm-metric-label">Shared Expenses</div>'
            f'<div class="fm-metric-value">{len(expenses)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">💰</div>'
            f'<div class="fm-metric-label">Your Total Share</div>'
            f'<div class="fm-metric-value">₹{total_share:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">👥</div>'
            f'<div class="fm-metric-label">Group Totals</div>'
            f'<div class="fm-metric-value">₹{total_expense:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Expense cards ──────────────────────────────────────────────
    st.markdown("### Shared Expenses")
    for e in expenses:
        _splitwise_card(e)

    # ── Import as personal expense ────────────────────────────────
    st.markdown("<hr class='fm-divider'>", unsafe_allow_html=True)
    st.markdown("#### Import to Personal Expenses")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Import your share of a Splitwise expense into FinMate's expense tracker.</p>",
        unsafe_allow_html=True,
    )

    options = {f"{e['description']} (₹{e['user_share']:,.0f})": i for i, e in enumerate(expenses)}
    selected_label = st.selectbox("Select expense to import", list(options.keys()))

    if st.button("📥  Import Selected Expense", use_container_width=True):
        idx = options[selected_label]
        sw  = expenses[idx]
        result = add_expense({
            "merchant": sw.get("description", "Splitwise Expense"),
            "amount":   sw.get("user_share", 0),
            "date":     sw.get("date", ""),
            "category": "Others",
            "payment":  "Splitwise",
            "notes":    f"Splitwise group: {sw.get('group', '')} | Paid by: {sw.get('paid_by', '')}",
            "source":   "splitwise",
        })
        if result.get("success"):
            st.success(
                f"✅ Imported '{sw.get('description')}' — "
                f"₹{sw.get('user_share', 0):,.2f} added to your expenses!"
            )
        else:
            st.error(f"Import failed: {result.get('message')}")

    # ── Table view ─────────────────────────────────────────────────
    with st.expander("📊 View as Table"):
        df = pd.DataFrame([{
            "Group":       e.get("group", ""),
            "Description": e.get("description", ""),
            "Total (₹)":   e.get("total", 0),
            "Your Share (₹)": e.get("user_share", 0),
            "Paid By":     e.get("paid_by", ""),
            "Date":        e.get("date", ""),
        } for e in expenses])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total (₹)":      st.column_config.NumberColumn(format="₹%.2f"),
                "Your Share (₹)": st.column_config.NumberColumn(format="₹%.2f"),
            },
        )


def _splitwise_card(e: dict) -> None:
    group       = e.get("group", "")
    description = e.get("description", "")
    total       = e.get("total", 0)
    user_share  = e.get("user_share", 0)
    paid_by     = e.get("paid_by", "")
    date        = e.get("date", "")
    pct         = user_share / total * 100 if total else 0

    st.markdown(
        f"""
        <div class="fm-expense-row">
            <div>
                <div class="fm-expense-merchant">{description}</div>
                <div class="fm-expense-meta">
                    👥 {group} &nbsp;·&nbsp; 📅 {date} &nbsp;·&nbsp;
                    💳 Paid by: <strong>{paid_by}</strong>
                </div>
                <div style="font-size:0.75rem; color:{COLORS['text_muted']}; margin-top:2px;">
                    Your share: {pct:.0f}% of total ₹{total:,.0f}
                </div>
            </div>
            <div style="text-align:right;">
                <div class="fm-expense-amount">₹{user_share:,.2f}</div>
                <div style="font-size:0.7rem; color:{COLORS['text_muted']};">your share</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
