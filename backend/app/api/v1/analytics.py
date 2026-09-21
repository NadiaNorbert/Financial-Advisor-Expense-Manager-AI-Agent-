"""
backend/app/api/v1/analytics.py
===============================
Analytics endpoints for spending summaries, trends, category breakdowns, and merchant stats.
"""

from __future__ import annotations
import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends

from backend.app.schemas.all_schemas import SpendingSummaryOut
from backend.app.core.security import get_current_user_optional
from backend.database import get_expenses
from backend.expenses.analyzer import analyze_spending
from backend.adapter import _to_frontend_cat

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=SpendingSummaryOut)
def get_summary(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else None
    
    all_expenses = get_expenses(limit=10_000, user_id=user_id)
    if not all_expenses:
        return SpendingSummaryOut(
            total_spending=0.0,
            monthly_spending=0.0,
            by_category={},
            monthly_trend=[],
            daily_spending=[],
            top_category="N/A",
            transaction_count=0,
        )
        
    analysis = analyze_spending(user_id=user_id)
    this_month = datetime.date.today().strftime("%Y-%m")
    
    monthly_total = sum(
        e["amount"] for e in all_expenses
        if str(e.get("date", "")).startswith(this_month)
    )
    
    raw_by_cat = analysis.get("by_category", {})
    by_cat_front: Dict[str, float] = {}
    for backend_cat, amt in raw_by_cat.items():
        front_cat = _to_frontend_cat(backend_cat)
        by_cat_front[front_cat] = round(by_cat_front.get(front_cat, 0.0) + amt, 2)
        
    top_cat = max(by_cat_front, key=by_cat_front.get) if by_cat_front else "N/A"
    
    monthly_map: Dict[str, float] = {}
    for e in all_expenses:
        m = str(e.get("date", ""))[:7]
        if m:
            monthly_map[m] = round(monthly_map.get(m, 0.0) + e["amount"], 2)
    monthly_trend = [
        {"month": m, "amount": a}
        for m, a in sorted(monthly_map.items())[-12:]
    ]
    
    daily_map: Dict[str, float] = {}
    for e in all_expenses:
        d = str(e.get("date", ""))[:10]
        if d:
            daily_map[d] = round(daily_map.get(d, 0.0) + e["amount"], 2)
    daily_spending = [
        {"date": d, "amount": a}
        for d, a in sorted(daily_map.items())[-60:]
    ]
    
    total_val = round(analysis.get("summary", {}).get("total", sum(e["amount"] for e in all_expenses)), 2)
    
    return SpendingSummaryOut(
        total_spending=total_val,
        monthly_spending=round(monthly_total, 2),
        by_category=by_cat_front,
        monthly_trend=monthly_trend,
        daily_spending=daily_spending,
        top_category=top_cat,
        transaction_count=len(all_expenses),
    )


@router.get("/deep-dive")
def get_deep_dive(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else None
    expenses = get_expenses(limit=10_000, user_id=user_id)
    analysis = analyze_spending(user_id=user_id)
    
    total_spending = sum(e["amount"] for e in expenses)
    
    # Category table
    by_cat_front: Dict[str, float] = {}
    for backend_cat, amt in analysis.get("by_category", {}).items():
        front_cat = _to_frontend_cat(backend_cat)
        by_cat_front[front_cat] = round(by_cat_front.get(front_cat, 0.0) + amt, 2)
        
    category_table = []
    for cat, amt in sorted(by_cat_front.items(), key=lambda x: x[1], reverse=True):
        cat_txs = [e for e in expenses if _to_frontend_cat(e.get("category", "Others")) == cat]
        avg = amt / len(cat_txs) if cat_txs else 0.0
        pct = (amt / total_spending * 100) if total_spending > 0 else 0.0
        category_table.append({
            "category": cat,
            "transactions": len(cat_txs),
            "total": round(amt, 2),
            "avg_per_txn": round(avg, 2),
            "pct_of_total": round(pct, 1),
        })
        
    # Payment method table
    pm_counts: Dict[str, Dict[str, Any]] = {}
    for e in expenses:
        pm = e.get("payment_method") or "Unknown"
        if pm not in pm_counts:
            pm_counts[pm] = {"count": 0, "total": 0.0}
        pm_counts[pm]["count"] += 1
        pm_counts[pm]["total"] += e.get("amount", 0.0)
        
    payment_methods_table = [
        {
            "payment_method": pm,
            "transactions": v["count"],
            "total_spent": round(v["total"], 2),
            "avg_amount": round(v["total"] / v["count"], 2) if v["count"] else 0.0,
        }
        for pm, v in sorted(pm_counts.items(), key=lambda x: x[1]["total"], reverse=True)
    ]
    
    return {
        "summary": analysis.get("summary", {}),
        "top_merchants": analysis.get("top_merchants", []),
        "daily_average": analysis.get("daily_average", 0.0),
        "highest_single_expense": analysis.get("highest_single_expense"),
        "category_table": category_table,
        "payment_methods_table": payment_methods_table,
    }
