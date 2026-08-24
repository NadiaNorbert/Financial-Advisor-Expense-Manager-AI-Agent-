"""
FinMate AI - Expense Card Component
=====================================
Renders individual styled expense rows used in expense lists and the dashboard.
"""

import streamlit as st
from frontend.styles import COLORS


# Map category name → CSS badge class
_BADGE_MAP: dict[str, str] = {
    "Food & Dining":  "badge-food",
    "Transport":      "badge-transport",
    "Shopping":       "badge-shopping",
    "Entertainment":  "badge-entertainment",
    "Utilities":      "badge-utilities",
    "Healthcare":     "badge-healthcare",
    "Education":      "badge-education",
    "Rent":           "badge-rent",
    "Others":         "badge-others",
}

# Source labels
_SOURCE_LABELS: dict[str, str] = {
    "manual":     "✍️ Manual",
    "screenshot": "📸 OCR",
    "csv":        "📄 CSV",
    "splitwise":  "🤝 Splitwise",
}


def _badge(category: str) -> str:
    css_class = _BADGE_MAP.get(category, "badge-others")
    return f'<span class="fm-badge {css_class}">{category}</span>'


def _source_tag(source: str) -> str:
    label = _SOURCE_LABELS.get(source, source)
    return (
        f'<span style="font-size:0.7rem; color:{COLORS["text_muted"]}; '
        f'background:rgba(148,163,184,0.12); padding:2px 7px; '
        f'border-radius:10px;">{label}</span>'
    )


def expense_card(expense: dict) -> None:
    """
    Render a single expense as a styled row card.

    Args:
        expense: dict with keys: merchant, amount, date, category, payment, source
    """
    merchant = expense.get("merchant", "Unknown")
    amount   = expense.get("amount", 0)
    date     = expense.get("date", "")
    category = expense.get("category", "Others")
    payment  = expense.get("payment", "")
    source   = expense.get("source", "manual")

    html = f"""
    <div class="fm-expense-row">
        <div>
            <div class="fm-expense-merchant">{merchant}</div>
            <div class="fm-expense-meta">
                {date} &nbsp;·&nbsp; {payment} &nbsp;·&nbsp;
                {_badge(category)} &nbsp;{_source_tag(source)}
            </div>
        </div>
        <div class="fm-expense-amount">₹{amount:,.2f}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def expense_card_list(expenses: list[dict], limit: int = 0) -> None:
    """
    Render a vertical list of expense cards.

    Args:
        expenses: list of expense dicts
        limit:    if > 0, only show the first `limit` items
    """
    items = expenses[:limit] if limit > 0 else expenses
    if not items:
        st.info("No expenses to display.")
        return
    for e in items:
        expense_card(e)
