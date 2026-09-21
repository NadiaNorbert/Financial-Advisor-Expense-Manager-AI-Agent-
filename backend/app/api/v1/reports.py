"""
backend/app/api/v1/reports.py
=============================
Reports export endpoints returning downloadable CSV and TXT files.
"""

from __future__ import annotations
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Response

from backend.app.core.security import get_current_user_optional
from backend.database import get_expenses
from backend.auth import get_goals as db_get_goals
from backend.budgeting.budget_engine import calculate_budget as engine_calculate
from backend.adapter import _db_row_to_frontend, _to_frontend_cat, get_spending_summary
from utils.export import (
    export_expenses_csv,
    export_budget_csv,
    export_goals_csv,
    export_summary_txt,
    report_filename,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/export/expenses")
def download_expenses_csv(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else None
    rows = get_expenses(limit=10_000, user_id=user_id)
    expenses = [_db_row_to_frontend(r) for r in rows]
    csv_bytes = export_expenses_csv(expenses)
    fname = report_filename("expenses", "csv")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/export/budget")
def download_budget_csv(
    month: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else None
    raw_calc = engine_calculate(month or datetime.date.today().strftime("%Y-%m"), user_id=user_id)
    
    # Translate category names
    translated_by_cat = []
    for r in raw_calc.get("by_category", []):
        translated_by_cat.append({
            "category": _to_frontend_cat(r["category"]),
            "budget": r["budget"],
            "spent": r["spent"],
            "remaining": r["remaining"],
            "pct": r["pct"],
            "over_budget": r["over_budget"],
        })
    raw_calc["by_category"] = translated_by_cat
    
    csv_bytes = export_budget_csv(raw_calc)
    fname = report_filename("budget", "csv")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/export/goals")
def download_goals_csv(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else 1
    goals = db_get_goals(user_id)
    csv_bytes = export_goals_csv(goals)
    fname = report_filename("goals", "csv")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/export/summary")
def download_summary_txt(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else None
    rows = get_expenses(limit=10_000, user_id=user_id)
    expenses = [_db_row_to_frontend(r) for r in rows]
    summary = get_spending_summary()
    raw_calc = engine_calculate(datetime.date.today().strftime("%Y-%m"), user_id=user_id)
    goals = db_get_goals(user_id or 1)
    
    txt_bytes = export_summary_txt(expenses, summary, raw_calc, goals)
    fname = report_filename("summary", "txt")
    return Response(
        content=txt_bytes,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
