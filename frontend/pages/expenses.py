"""
FinMate AI - Expenses Page
============================
Searchable, filterable expense table with inline edit and delete.
"""

from __future__ import annotations

import datetime
import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from frontend.components.expense_card import expense_card
from backend.adapter import (
    get_all_expenses,
    update_expense,
    delete_expense,
    add_expense,
    CATEGORIES,
    PAYMENT_METHODS,
)


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>💳 Expenses</h1>", unsafe_allow_html=True)

    expenses = get_all_expenses()

    # ── Tabs: List / Add ───────────────────────────────────────────
    tab_list, tab_add = st.tabs(["📋  Expense List", "➕  Add Expense"])

    with tab_list:
        _expense_list(expenses)

    with tab_add:
        _add_expense_form()


# ---------------------------------------------------------------------------
# Expense list with filters
# ---------------------------------------------------------------------------

def _expense_list(expenses: list[dict]) -> None:
    if not expenses:
        st.info("No expenses recorded yet. Use the **Add Expense** tab to get started.")
        return

    # ── Filters ──────────────────────────────────────────────────
    with st.expander("🔍 Filter & Search", expanded=True):
        f1, f2, f3 = st.columns([2, 2, 1.5])

        with f1:
            search = st.text_input(
                "Search merchant",
                placeholder="e.g. Swiggy",
                label_visibility="collapsed",
            ).strip().lower()

        all_cats = ["All Categories"] + sorted({e.get("category", "Others") for e in expenses})
        with f2:
            cat_filter = st.selectbox("Category", all_cats, label_visibility="collapsed")

        # Date range
        dates = [str(e.get("date", "")) for e in expenses if e.get("date")]
        min_date = datetime.date.fromisoformat(min(dates)) if dates else datetime.date.today()
        max_date = datetime.date.fromisoformat(max(dates)) if dates else datetime.date.today()

        f4, f5 = st.columns(2)
        with f4:
            date_from = st.date_input("From", value=min_date, key="exp_from")
        with f5:
            date_to   = st.date_input("To",   value=max_date, key="exp_to")

        with f3:
            amounts   = [e.get("amount", 0) for e in expenses]
            max_amt   = int(max(amounts)) + 1 if amounts else 10000
            amt_range = st.slider(
                "Amount range (₹)",
                min_value=0,
                max_value=max_amt,
                value=(0, max_amt),
            )

    # ── Apply filters ─────────────────────────────────────────────
    filtered = expenses
    if search:
        filtered = [e for e in filtered if search in e.get("merchant", "").lower()]
    if cat_filter != "All Categories":
        filtered = [e for e in filtered if e.get("category") == cat_filter]
    filtered = [
        e for e in filtered
        if amt_range[0] <= e.get("amount", 0) <= amt_range[1]
    ]
    filtered = [
        e for e in filtered
        if date_from <= datetime.date.fromisoformat(str(e.get("date", date_from))[:10]) <= date_to
    ]

    # Sort by date descending
    filtered = sorted(filtered, key=lambda x: str(x.get("date", "")), reverse=True)

    # ── Summary row ───────────────────────────────────────────────
    total_shown = sum(e.get("amount", 0) for e in filtered)
    m1, m2, m3 = st.columns(3)
    m1.metric("Matching Transactions", len(filtered))
    m2.metric("Total Spending",        f"₹{total_shown:,.2f}")
    m3.metric(
        "Avg per Transaction",
        f"₹{total_shown / len(filtered):,.2f}" if filtered else "₹0.00",
    )

    st.markdown("<hr class='fm-divider'>", unsafe_allow_html=True)

    # ── View toggle ───────────────────────────────────────────────
    view_col, sort_col = st.columns([3, 1])
    with view_col:
        view_mode = st.radio(
            "View as",
            ["Cards", "Table"],
            horizontal=True,
            label_visibility="collapsed",
        )
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            ["Date ↓", "Date ↑", "Amount ↓", "Amount ↑", "Merchant"],
            label_visibility="collapsed",
        )

    # Apply sort
    if sort_by == "Date ↓":
        filtered = sorted(filtered, key=lambda x: str(x.get("date", "")), reverse=True)
    elif sort_by == "Date ↑":
        filtered = sorted(filtered, key=lambda x: str(x.get("date", "")))
    elif sort_by == "Amount ↓":
        filtered = sorted(filtered, key=lambda x: x.get("amount", 0), reverse=True)
    elif sort_by == "Amount ↑":
        filtered = sorted(filtered, key=lambda x: x.get("amount", 0))
    elif sort_by == "Merchant":
        filtered = sorted(filtered, key=lambda x: x.get("merchant", "").lower())

    if not filtered:
        st.warning("No expenses match your filters.")
        return

    # ── Render ────────────────────────────────────────────────────
    if view_mode == "Cards":
        _render_cards(filtered)
    else:
        _render_table(filtered)


def _render_cards(expenses: list[dict]) -> None:
    """Render expenses as styled cards with edit/delete buttons."""
    for e in expenses:
        col_card, col_edit, col_del = st.columns([8, 1, 1])

        with col_card:
            expense_card(e)

        with col_edit:
            if st.button("✏️", key=f"edit_{e['id']}", help="Edit expense"):
                st.session_state[f"editing_{e['id']}"] = True

        with col_del:
            if st.button("🗑️", key=f"del_{e['id']}", help="Delete expense"):
                result = delete_expense(e["id"])
                if result["success"]:
                    st.success(f"Deleted: {e['merchant']}")
                    st.rerun()
                else:
                    st.error(result["message"])

        # Inline edit form
        if st.session_state.get(f"editing_{e['id']}", False):
            _inline_edit_form(e)


def _inline_edit_form(e: dict) -> None:
    """Show an inline edit form for a given expense."""
    with st.form(f"edit_form_{e['id']}"):
        st.markdown(f"**Editing: {e['merchant']}**")
        c1, c2 = st.columns(2)
        with c1:
            new_merchant = st.text_input("Merchant", value=e.get("merchant", ""))
        with c2:
            new_amount = st.number_input(
                "Amount (₹)", min_value=0.01,
                value=float(e.get("amount", 0)), format="%.2f"
            )
        c3, c4 = st.columns(2)
        with c3:
            new_date = st.date_input(
                "Date",
                value=datetime.date.fromisoformat(str(e.get("date", datetime.date.today()))[:10]),
            )
        with c4:
            cat_idx = CATEGORIES.index(e.get("category", "Others")) if e.get("category") in CATEGORIES else 0
            new_cat = st.selectbox("Category", CATEGORIES, index=cat_idx)
        c5, c6 = st.columns(2)
        with c5:
            pay_idx = PAYMENT_METHODS.index(e.get("payment", "UPI")) if e.get("payment") in PAYMENT_METHODS else 0
            new_pay = st.selectbox("Payment", PAYMENT_METHODS, index=pay_idx)
        with c6:
            new_notes = st.text_input("Notes", value=e.get("notes", ""))

        col_save, col_cancel = st.columns(2)
        with col_save:
            save = st.form_submit_button("💾 Save", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("✕ Cancel", use_container_width=True)

    if save:
        result = update_expense(e["id"], {
            "merchant": new_merchant,
            "amount":   new_amount,
            "date":     str(new_date),
            "category": new_cat,
            "payment":  new_pay,
            "notes":    new_notes,
        })
        if result["success"]:
            st.success("Updated successfully.")
            st.session_state[f"editing_{e['id']}"] = False
            st.rerun()
        else:
            st.error(result["message"])

    if cancel:
        st.session_state[f"editing_{e['id']}"] = False
        st.rerun()


def _render_table(expenses: list[dict]) -> None:
    """Render expenses as a Pandas DataFrame table."""
    rows = []
    for e in expenses:
        rows.append({
            "Date":    e.get("date", ""),
            "Merchant": e.get("merchant", ""),
            "Category": e.get("category", ""),
            "Amount (₹)": e.get("amount", 0),
            "Payment": e.get("payment", ""),
            "Source":  e.get("source", ""),
            "_id":     e.get("id"),
        })

    df = pd.DataFrame(rows)
    display_df = df.drop(columns=["_id"])

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount (₹)": st.column_config.NumberColumn(format="₹%.2f"),
            "Date":       st.column_config.DateColumn(),
        },
    )

    # Download filtered data
    from utils.export import export_expenses_csv, report_filename
    csv_bytes = export_expenses_csv(expenses)
    st.download_button(
        "⬇️  Export Filtered Data (CSV)",
        data=csv_bytes,
        file_name=report_filename("expenses_filtered", "csv"),
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Add expense form (duplicate from upload page for convenience)
# ---------------------------------------------------------------------------

def _add_expense_form() -> None:
    st.markdown("#### Add New Expense")

    with st.form("expenses_add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            merchant = st.text_input("Merchant *", placeholder="e.g. Zomato")
        with c2:
            amount = st.number_input("Amount (₹) *", min_value=0.01, step=0.5, format="%.2f")

        c3, c4 = st.columns(2)
        with c3:
            date = st.date_input("Date *", value=datetime.date.today())
        with c4:
            category = st.selectbox("Category *", CATEGORIES)

        c5, c6 = st.columns(2)
        with c5:
            payment = st.selectbox("Payment Method *", PAYMENT_METHODS)
        with c6:
            notes = st.text_input("Notes", placeholder="Optional")

        submitted = st.form_submit_button("✅  Save Expense", use_container_width=True)

    if submitted:
        if not merchant.strip():
            st.error("Merchant name is required.")
            return
        if amount <= 0:
            st.error("Amount must be greater than zero.")
            return

        result = add_expense({
            "merchant": merchant.strip(),
            "amount":   round(float(amount), 2),
            "date":     str(date),
            "category": category,
            "payment":  payment,
            "notes":    notes.strip(),
            "source":   "manual",
        })
        if result.get("success"):
            st.success(f"✅ {merchant} — ₹{amount:,.2f} saved! (ID #{result.get('id', '?')})")
            st.balloons()
        elif result.get("duplicate"):
            st.warning(f"⚠️ Duplicate expense — not saved. {result.get('message', '')}")
        else:
            st.error(f"Error: {result.get('message')}")
