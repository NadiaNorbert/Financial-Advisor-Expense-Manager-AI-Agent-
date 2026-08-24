"""
budget_engine.py – Budget calculation and management
======================================================
Bridges the Streamlit frontend budget UI with the SQLite persistence layer.

Public API
----------
    calculate_budget(month: str | None = None) -> dict
    get_budget_settings(month: str | None = None) -> dict
    save_budget_settings(income: float, budgets: dict, month: str | None = None) -> dict
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from backend.database import (
    get_budget,
    save_budget,
    get_category_totals,
    get_expenses,
)
from backend.config import EXPENSE_CATEGORIES

logger = logging.getLogger(__name__)


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def get_budget_settings(month: Optional[str] = None, user_id: int | None = None) -> dict:
    month = month or _current_month()
    saved = get_budget(month, user_id=user_id)
    income   = saved.get("income", 0.0)
    budgets  = saved.get("categories", {})
    full_budgets = {cat: budgets.get(cat, 0.0) for cat in EXPENSE_CATEGORIES}
    return {"income": income, "budgets": full_budgets}


def save_budget_settings(
    income: float,
    budgets: dict,
    month: Optional[str] = None,
    user_id: int | None = None,
) -> dict:
    month = month or _current_month()
    try:
        active = {cat: amt for cat, amt in budgets.items() if amt > 0}
        save_budget(month, income, active, user_id=user_id)
        logger.info("Budget saved for %s — income=₹%.2f, categories=%d", month, income, len(active))
        return {"success": True, "message": f"Budget saved for {month}."}
    except Exception as e:
        logger.error("save_budget_settings failed: %s", e)
        return {"success": False, "message": str(e)}


def calculate_budget(month: Optional[str] = None, user_id: int | None = None) -> dict:
    """Calculate full budget vs actual for the given month.

    Returns
    -------
    dict
        Keys:
        - ``income``            : float
        - ``total_budget``      : float  (sum of all category budgets)
        - ``total_spent``       : float  (actual spending this month)
        - ``remaining``         : float  (total_budget – total_spent)
        - ``savings_estimate``  : float  (income – total_spent)
        - ``by_category``       : list[dict] — one dict per category with:
            - ``category``      : str
            - ``budget``        : float
            - ``spent``         : float
            - ``remaining``     : float
            - ``pct``           : float  (spent / budget * 100, capped at 100)
            - ``over_budget``   : bool
    """
    month = month or _current_month()
    start_date = f"{month}-01"

    year, mon = map(int, month.split("-"))
    import calendar
    last_day = calendar.monthrange(year, mon)[1]
    end_date = f"{month}-{last_day:02d}"

    settings     = get_budget_settings(month, user_id=user_id)
    income       = settings["income"]
    budgets      = settings["budgets"]
    spent_by_cat = get_category_totals(start_date=start_date, end_date=end_date, user_id=user_id)

    total_budget = sum(v for v in budgets.values() if v > 0)
    total_spent  = sum(spent_by_cat.values())
    remaining    = total_budget - total_spent
    savings_est  = income - total_spent if income else None

    by_category = []
    for cat in EXPENSE_CATEGORIES:
        budget = budgets.get(cat, 0.0)
        spent  = spent_by_cat.get(cat, 0.0)
        rem    = budget - spent
        pct    = round(spent / budget * 100, 1) if budget > 0 else 0.0
        by_category.append({
            "category":   cat,
            "budget":     round(budget, 2),
            "spent":      round(spent, 2),
            "remaining":  round(rem, 2),
            "pct":        pct,
            "over_budget": spent > budget and budget > 0,
        })

    return {
        "income":           round(income, 2),
        "total_budget":     round(total_budget, 2),
        "total_spent":      round(total_spent, 2),
        "remaining":        round(remaining, 2),
        "savings_estimate": round(savings_est, 2) if savings_est is not None else 0.0,
        "by_category":      by_category,
    }
