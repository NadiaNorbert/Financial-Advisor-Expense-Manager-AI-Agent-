"""
FinMate AI - Split Expenses Page
==================================
Manual expense splitting — split any expense among friends/group members
and import your share directly into the expense tracker.
No external API required.
"""

from __future__ import annotations

import datetime
import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from backend.adapter import add_expense, CATEGORIES, PAYMENT_METHODS


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>🤝 Split Expenses</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Split a shared expense among friends and import your share into your tracker.</p>",
        unsafe_allow_html=True,
    )

    tab_split, tab_history = st.tabs(["➗  Split an Expense", "📋  Split History"])

    with tab_split:
        _split_tab()

    with tab_history:
        _history_tab()


# ---------------------------------------------------------------------------
# Tab 1 — Split Calculator
# ---------------------------------------------------------------------------

def _split_tab() -> None:
    st.markdown("#### New Split Expense")

    # ── Expense details ────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        description = st.text_input("Expense Description *", placeholder="e.g. Dinner at Barbeque Nation")
    with col2:
        total_amount = st.number_input("Total Amount (₹) *", min_value=0.01, step=10.0, format="%.2f")

    col3, col4 = st.columns(2)
    with col3:
        date = st.date_input("Date", value=datetime.date.today())
    with col4:
        category = st.selectbox("Category", CATEGORIES)

    col5, col6 = st.columns(2)
    with col5:
        payment = st.selectbox("Payment Method", PAYMENT_METHODS)
    with col6:
        paid_by = st.text_input("Paid By", placeholder="e.g. You / Rahul")

    st.markdown("---")

    # ── Members ────────────────────────────────────────────────────
    st.markdown("#### Split Among")

    num_members = st.number_input("Number of people (including you)", min_value=2, max_value=20, value=2, step=1)

    members = []
    split_mode = st.radio("Split Mode", ["Equal Split", "Custom Amounts"], horizontal=True)

    if split_mode == "Equal Split":
        your_share = round(total_amount / num_members, 2) if num_members else 0
        st.markdown(
            f"""
            <div style="
                background:{COLORS['bg_card']};
                border:1px solid {COLORS['border']};
                border-radius:10px;
                padding:1rem 1.5rem;
                text-align:center;
                margin:0.5rem 0 1rem 0;
            ">
                <div style="font-size:0.85rem; color:{COLORS['text_muted']};">Your share ({num_members} people)</div>
                <div style="font-size:2rem; font-weight:700; color:{COLORS['accent_teal']};">
                    ₹{your_share:,.2f}
                </div>
                <div style="font-size:0.75rem; color:{COLORS['text_muted']};">
                    = ₹{total_amount:,.2f} ÷ {num_members}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Collect member names for reference
        st.markdown("**Member names (optional, for your reference):**")
        name_cols = st.columns(min(num_members, 4))
        for i in range(num_members):
            col = name_cols[i % len(name_cols)]
            label = "You" if i == 0 else f"Person {i + 1}"
            name = col.text_input(label, key=f"member_{i}", placeholder=label)
            members.append({"name": name or label, "share": your_share})

    else:  # Custom amounts
        st.markdown("**Enter each person's share:**")
        total_assigned = 0.0
        name_cols = st.columns(min(num_members, 4))
        custom_shares = []
        for i in range(num_members):
            col = name_cols[i % len(name_cols)]
            default_share = round(total_amount / num_members, 2)
            label = "You" if i == 0 else f"Person {i + 1}"
            name = col.text_input(f"Name ({label})", key=f"cname_{i}", placeholder=label)
            share = col.number_input(f"Share (₹)", key=f"cshare_{i}",
                                     min_value=0.0, value=float(default_share), step=1.0, format="%.2f")
            custom_shares.append(share)
            members.append({"name": name or label, "share": share})
            total_assigned += share

        remaining = round(total_amount - total_assigned, 2)
        color = COLORS["accent_green"] if abs(remaining) < 0.01 else COLORS["accent_red"]
        st.markdown(
            f"<p style='color:{color}; font-size:0.85rem;'>"
            f"Assigned: ₹{total_assigned:,.2f} / ₹{total_amount:,.2f} "
            f"({'✅ balanced' if abs(remaining) < 0.01 else f'⚠️ ₹{abs(remaining):,.2f} remaining'})"
            f"</p>",
            unsafe_allow_html=True,
        )

        your_share = members[0]["share"] if members else 0.0

    # ── Import button ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    notes = st.text_input(
        "Notes (optional)",
        placeholder=f"Split with {num_members} people",
    )

    if st.button("💾  Import My Share", use_container_width=True, type="primary"):
        if not description.strip():
            st.error("Please enter an expense description.")
        elif total_amount <= 0:
            st.error("Total amount must be greater than zero.")
        elif your_share <= 0:
            st.error("Your share must be greater than zero.")
        else:
            member_names = ", ".join(m["name"] for m in members[1:]) if len(members) > 1 else ""
            auto_notes = notes.strip() or f"Split {num_members} ways" + (f" with {member_names}" if member_names else "")
            if paid_by:
                auto_notes += f" | Paid by: {paid_by}"

            expense = {
                "merchant": description.strip(),
                "amount":   round(your_share, 2),
                "date":     str(date),
                "category": category,
                "payment":  payment,
                "notes":    auto_notes,
                "source":   "splitwise",
            }
            result = add_expense(expense)

            if result.get("success"):
                # Save to split history in session state
                if "split_history" not in st.session_state:
                    st.session_state.split_history = []
                st.session_state.split_history.insert(0, {
                    "description": description.strip(),
                    "total":       round(total_amount, 2),
                    "your_share":  round(your_share, 2),
                    "members":     num_members,
                    "paid_by":     paid_by,
                    "date":        str(date),
                    "category":    category,
                })
                st.success(
                    f"✅ **{description}** — your share of ₹{your_share:,.2f} "
                    f"added to expenses! (ID #{result.get('id', '?')})"
                )
                st.balloons()
            else:
                st.error(f"Could not save: {result.get('message')}")


# ---------------------------------------------------------------------------
# Tab 2 — Split History (session-based)
# ---------------------------------------------------------------------------

def _history_tab() -> None:
    history = st.session_state.get("split_history", [])

    if not history:
        st.markdown(
            f"""
            <div style="
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                padding: 2.5rem;
                text-align: center;
                color: {COLORS['text_muted']};
                margin-top: 1rem;
            ">
                <div style="font-size:2.5rem; margin-bottom:0.5rem;">🤝</div>
                <div style="font-size:1rem; font-weight:600; margin-bottom:4px;">
                    No splits yet this session
                </div>
                <div style="font-size:0.82rem;">
                    Use the "Split an Expense" tab to split and import shared expenses.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    total_shared = sum(h["your_share"] for h in history)
    c1, c2 = st.columns(2)
    c1.metric("Splits This Session", len(history))
    c2.metric("Your Total Share", f"₹{total_shared:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    df = pd.DataFrame([{
        "Date":        h["date"],
        "Description": h["description"],
        "Total (₹)":   h["total"],
        "Your Share (₹)": h["your_share"],
        "# People":    h["members"],
        "Paid By":     h.get("paid_by", ""),
        "Category":    h.get("category", ""),
    } for h in history])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total (₹)":      st.column_config.NumberColumn(format="₹%.2f"),
            "Your Share (₹)": st.column_config.NumberColumn(format="₹%.2f"),
        },
    )
