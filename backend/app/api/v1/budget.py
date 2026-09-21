"""
backend/app/api/v1/budget.py
============================
Budget management endpoints: settings, calculation, and progress tracking.
"""

from __future__ import annotations
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.schemas.all_schemas import (
    BudgetSettingsIn,
    BudgetSettingsOut,
    BudgetCalculationOut,
    CategoryBudgetRow,
)
from backend.app.core.security import get_current_user_optional
from backend.budgeting.budget_engine import (
    get_budget_settings as engine_get_settings,
    save_budget_settings as engine_save_settings,
    calculate_budget as engine_calculate,
)
from backend.adapter import (
    _to_backend_cat,
    _to_frontend_cat,
    CATEGORIES,
)

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("/settings", response_model=BudgetSettingsOut)
def get_settings(
    month: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    target_month = month or date.today().strftime("%Y-%m")
    user_id = current_user["id"] if current_user else None
    raw = engine_get_settings(target_month, user_id=user_id)
    
    front_budgets: dict[str, float] = {}
    for backend_cat, amt in raw.get("budgets", {}).items():
        front_cat = _to_frontend_cat(backend_cat)
        front_budgets[front_cat] = round(front_budgets.get(front_cat, 0.0) + amt, 2)
        
    full = {cat: front_budgets.get(cat, 0.0) for cat in CATEGORIES}
    return {
        "income": raw.get("income", 0.0),
        "budgets": full,
        "month": target_month,
    }


@router.post("/settings", response_model=BudgetSettingsOut)
def save_settings(
    data: BudgetSettingsIn,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    target_month = data.month or date.today().strftime("%Y-%m")
    user_id = current_user["id"] if current_user else None
    
    backend_budgets = {
        _to_backend_cat(cat): amt
        for cat, amt in data.budgets.items()
        if amt > 0
    }
    
    res = engine_save_settings(data.income, backend_budgets, month=target_month, user_id=user_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message", "Failed to save budget"))
        
    full = {cat: data.budgets.get(cat, 0.0) for cat in CATEGORIES}
    return {
        "income": data.income,
        "budgets": full,
        "month": target_month,
    }


@router.get("/calculate", response_model=BudgetCalculationOut)
def calculate_budget(
    month: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    target_month = month or date.today().strftime("%Y-%m")
    user_id = current_user["id"] if current_user else None
    raw = engine_calculate(target_month, user_id=user_id)
    
    translated_rows: list[CategoryBudgetRow] = []
    merged: dict[str, dict] = {}
    
    for row in raw.get("by_category", []):
        front = _to_frontend_cat(row["category"])
        if front not in merged:
            merged[front] = {
                "category": front,
                "budget": 0.0,
                "spent": 0.0,
                "remaining": 0.0,
            }
        merged[front]["budget"] += row["budget"]
        merged[front]["spent"] += row["spent"]
        
    for m in merged.values():
        budget = round(m["budget"], 2)
        spent = round(m["spent"], 2)
        rem = round(budget - spent, 2)
        pct = round(spent / budget * 100, 1) if budget > 0 else 0.0
        over = spent > budget and budget > 0
        translated_rows.append(CategoryBudgetRow(
            category=m["category"],
            budget=budget,
            spent=spent,
            remaining=rem,
            pct=pct,
            over_budget=over,
        ))
        
    # Ensure every frontend category is present
    present = {r.category for r in translated_rows}
    for cat in CATEGORIES:
        if cat not in present:
            translated_rows.append(CategoryBudgetRow(
                category=cat,
                budget=0.0,
                spent=0.0,
                remaining=0.0,
                pct=0.0,
                over_budget=False,
            ))
            
    return BudgetCalculationOut(
        income=raw.get("income", 0.0),
        total_budget=raw.get("total_budget", 0.0),
        total_spent=raw.get("total_spent", 0.0),
        remaining=raw.get("remaining", 0.0),
        savings_estimate=raw.get("savings_estimate", 0.0),
        by_category=translated_rows,
        month=target_month,
    )
