"""
analyzer.py – Spending analysis utilities
==========================================
Provides summary and analysis functions over stored expenses.

Public API
----------
    get_spending_summary(start_date, end_date) -> dict
    get_category_summary(start_date, end_date) -> dict
    analyze_spending(start_date, end_date) -> dict
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from backend.database import get_expenses, get_category_totals, get_total_spending

logger = logging.getLogger(__name__)


def get_spending_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: int | None = None,
) -> dict:
    if not start_date and not end_date:
        start_date = date.today().strftime("%Y-%m-01")
        end_date = date.today().isoformat()

    expenses = get_expenses(start_date=start_date, end_date=end_date, limit=10_000, user_id=user_id)
    total = round(sum(e["amount"] for e in expenses), 2)
    count = len(expenses)
    average = round(total / count, 2) if count else 0.0

    return {
        "total": total,
        "count": count,
        "average": average,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_category_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: int | None = None,
) -> dict:
    if not start_date and not end_date:
        start_date = date.today().strftime("%Y-%m-01")
        end_date = date.today().isoformat()

    return get_category_totals(start_date=start_date, end_date=end_date, user_id=user_id)


def analyze_spending(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: int | None = None,
) -> dict:
    if not start_date and not end_date:
        start_date = date.today().strftime("%Y-%m-01")
        end_date = date.today().isoformat()

    expenses = get_expenses(start_date=start_date, end_date=end_date, limit=10_000, user_id=user_id)

    if not expenses:
        return {
            "summary": {"total": 0.0, "count": 0, "average": 0.0},
            "by_category": {},
            "top_merchants": [],
            "daily_average": 0.0,
            "highest_single_expense": None,
        }

    total = round(sum(e["amount"] for e in expenses), 2)
    count = len(expenses)

    merchant_totals: dict[str, float] = {}
    for e in expenses:
        merchant_totals[e["merchant"]] = round(
            merchant_totals.get(e["merchant"], 0) + e["amount"], 2
        )
    top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    unique_days = len({e["date"] for e in expenses})
    daily_average = round(total / unique_days, 2) if unique_days else 0.0

    highest = max(expenses, key=lambda e: e["amount"])

    by_category = get_category_totals(start_date=start_date, end_date=end_date, user_id=user_id)

    return {
        "summary": {
            "total": total,
            "count": count,
            "average": round(total / count, 2),
            "start_date": start_date,
            "end_date": end_date,
        },
        "by_category": by_category,
        "top_merchants": [{"merchant": m, "total": t} for m, t in top_merchants],
        "daily_average": daily_average,
        "highest_single_expense": {
            "merchant": highest["merchant"],
            "amount": highest["amount"],
            "date": highest["date"],
            "category": highest["category"],
        },
    }
