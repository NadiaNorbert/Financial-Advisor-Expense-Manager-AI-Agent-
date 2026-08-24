"""
FinMate AI - Backend Adapter Layer
===================================
Single source of truth for all frontend ↔ backend communication.

Design rules
------------
- Every function calls the REAL backend directly.
- There is NO mock fallback for functions that the real backend implements.
- Session-state in-memory fallbacks are kept ONLY for Goals and Splitwise,
  which have no backend module yet.
- Field names are normalised here so neither the frontend nor the backend
  needs to change:
    DB column   : payment_method  →  frontend field : payment
    DB category : "Food"          →  frontend field : "Food & Dining"   (etc.)
- OCR takes bytes from the file uploader; backend takes a file path.
  The adapter writes a temp file, calls the backend, then deletes it.
"""

from __future__ import annotations

import datetime
import logging
import os
import tempfile
from typing import Any

logger = logging.getLogger(__name__)


# ===========================================================================
# Category mapping
# ===========================================================================
# Backend (config.EXPENSE_CATEGORIES) → Frontend display name
# Keep this as the single source; everything else is derived from it.

_BACKEND_TO_FRONTEND: dict[str, str] = {
    "Food":          "Food & Dining",
    "Groceries":     "Food & Dining",   # merge into one UI bucket
    "Transport":     "Transport",
    "Shopping":      "Shopping",
    "Entertainment": "Entertainment",
    "Bills":         "Bills & Utilities",
    "Utilities":     "Bills & Utilities",
    "Healthcare":    "Healthcare",
    "Education":     "Education",
    "Travel":        "Travel",
    "Rent":          "Rent",
    "Others":        "Others",
}

_FRONTEND_TO_BACKEND: dict[str, str] = {
    "Food & Dining":    "Food",
    "Transport":        "Transport",
    "Shopping":         "Shopping",
    "Entertainment":    "Entertainment",
    "Bills & Utilities":"Bills",
    "Healthcare":       "Healthcare",
    "Education":        "Education",
    "Travel":           "Travel",
    "Rent":             "Rent",
    "Others":           "Others",
}

# The canonical list shown in every selectbox / filter
CATEGORIES: list[str] = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Rent",
    "Others",
]

PAYMENT_METHODS: list[str] = [
    "UPI", "Credit Card", "Debit Card", "Cash",
    "Net Banking", "Wallet", "Other",
]

# Guru names for the AI Advisor page
GURU_PROMPTS: dict[str, str] = {
    "General Financial Principles": "using universal personal finance principles",
    "Warren Buffett":               "using Warren Buffett's value investing and frugality philosophy",
    "Robert Kiyosaki":              "using Robert Kiyosaki's Rich Dad Poor Dad philosophy about assets and liabilities",
    "Ramit Sethi":                  "using Ramit Sethi's I Will Teach You To Be Rich philosophy focused on automation and conscious spending",
}


def _get_user_id() -> int | None:
    """Get the current logged-in user's id from Streamlit session state."""
    try:
        import streamlit as st
        return st.session_state.get("user_id")
    except Exception:
        return None


def _to_frontend_cat(backend_cat: str) -> str:
    return _BACKEND_TO_FRONTEND.get(backend_cat, backend_cat)


def _to_backend_cat(frontend_cat: str) -> str:
    return _FRONTEND_TO_BACKEND.get(frontend_cat, "Others")

def _db_row_to_frontend(row: dict) -> dict:
    """Convert a raw database row to the shape the frontend expects."""
    return {
        "id":       row.get("id"),
        "merchant": row.get("merchant", ""),
        "amount":   row.get("amount", 0.0),
        "date":     row.get("date", ""),
        "category": _to_frontend_cat(row.get("category", "Others")),
        "payment":  row.get("payment_method") or row.get("payment") or "Other",
        "source":   row.get("source") or "manual",
        "notes":    row.get("notes") or "",
    }


def _frontend_to_db_row(expense: dict) -> dict:
    """Convert a frontend expense dict to the shape database.add_expense expects."""
    return {
        "merchant":       expense.get("merchant", ""),
        "amount":         float(expense.get("amount", 0)),
        "date":           str(expense.get("date", datetime.date.today())),
        "category":       _to_backend_cat(expense.get("category", "Others")),
        "payment_method": expense.get("payment") or expense.get("payment_method") or "Other",
        "source":         expense.get("source", "manual"),
        "notes":          expense.get("notes") or None,
    }


# ===========================================================================
# OCR
# ===========================================================================

def extract_expense_from_image(image_bytes: bytes) -> dict:
    """
    Frontend passes raw bytes from st.file_uploader.
    Backend expects a file path — write to a temp file, call backend, clean up.

    Returns frontend-shaped dict:
        {merchant, amount, date, payment_method, confidence, raw_text, error, _mock}
    """
    from backend.ocr.expense_ocr import extract_expense_from_image as _ocr

    suffix = ".png"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        result = _ocr(tmp_path)
    except Exception as e:
        logger.error("OCR adapter error: %s", e)
        result = {"error": str(e), "confidence": 0.0, "raw_text": ""}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return result


# ===========================================================================
# Expense categoriser
# ===========================================================================

def categorize_expense(merchant: str, amount: float = 0) -> str:
    """Return a FRONTEND category string for the given merchant name."""
    from backend.expenses.categorizer import categorize_expense as _cat
    result = _cat(merchant)
    return _to_frontend_cat(result["category"])


# ===========================================================================
# Expense CRUD
# ===========================================================================

def add_expense(expense: dict) -> dict:
    """
    Input : frontend expense dict  (uses 'payment' key)
    Output: {success, id, message}
    """
    from backend.database import add_expense as _add
    try:
        db_row   = _frontend_to_db_row(expense)
        new_id   = _add(db_row, user_id=_get_user_id())
        return {"success": True, "id": new_id, "message": "Expense saved."}
    except Exception as e:
        logger.error("add_expense failed: %s", e)
        return {"success": False, "id": None, "message": str(e)}


def update_expense(expense_id: int, updated: dict) -> dict:
    """
    Input : expense_id, dict of updated fields (frontend field names)
    Output: {success, message}
    """
    from backend.database import update_expense as _upd
    try:
        db_updates: dict[str, Any] = {}
        if "merchant"  in updated: db_updates["merchant"]       = updated["merchant"]
        if "amount"    in updated: db_updates["amount"]         = float(updated["amount"])
        if "date"      in updated: db_updates["date"]           = str(updated["date"])
        if "category"  in updated: db_updates["category"]       = _to_backend_cat(updated["category"])
        if "payment"   in updated: db_updates["payment_method"] = updated["payment"]
        if "notes"     in updated: db_updates["notes"]          = updated["notes"]

        ok = _upd(expense_id, db_updates)
        if ok:
            return {"success": True,  "message": "Expense updated."}
        return {"success": False, "message": f"No expense found with id={expense_id}."}
    except Exception as e:
        logger.error("update_expense failed: %s", e)
        return {"success": False, "message": str(e)}


def delete_expense(expense_id: int) -> dict:
    """Output: {success, message}"""
    from backend.database import delete_expense as _del
    try:
        ok = _del(expense_id)
        if ok:
            return {"success": True,  "message": "Expense deleted."}
        return {"success": False, "message": f"No expense found with id={expense_id}."}
    except Exception as e:
        logger.error("delete_expense failed: %s", e)
        return {"success": False, "message": str(e)}


def get_all_expenses() -> list[dict]:
    """Return all expenses for the current user, newest first."""
    from backend.database import get_expenses as _get
    try:
        rows = _get(limit=5000, user_id=_get_user_id())
        return [_db_row_to_frontend(r) for r in rows]
    except Exception as e:
        logger.error("get_all_expenses failed: %s", e)
        return []


def import_csv_expenses(df) -> dict:
    """
    Import a pandas DataFrame of transactions into the database.
    Auto-maps common column name variations.
    Output: {success, imported, skipped, message}
    """
    from backend.database import add_expense as _add
    import pandas as pd

    imported = skipped = 0
    for _, row in df.iterrows():
        try:
            merchant = str(
                row.get("merchant") or row.get("Merchant") or
                row.get("description") or row.get("Description") or "Unknown"
            ).strip()
            amount = float(
                str(row.get("amount") or row.get("Amount") or
                    row.get("debit") or row.get("Debit") or 0)
                .replace(",", "")
            )
            if amount <= 0 or merchant.lower() in ("", "unknown"):
                skipped += 1
                continue

            raw_date = str(
                row.get("date") or row.get("Date") or
                row.get("transaction_date") or datetime.date.today()
            ).strip()
            # Normalise date
            norm_date = _normalise_date(raw_date)

            frontend_cat = str(
                row.get("category") or row.get("Category") or
                categorize_expense(merchant)
            ).strip()
            backend_cat = _to_backend_cat(frontend_cat)

            payment = str(
                row.get("payment") or row.get("Payment") or
                row.get("payment_method") or "Other"
            ).strip()

            _add({
                "merchant":       merchant,
                "amount":         round(amount, 2),
                "date":           norm_date,
                "category":       backend_cat,
                "payment_method": payment,
                "source":         "csv",
                "notes":          None,
            }, user_id=_get_user_id())
            imported += 1
        except Exception as e:
            logger.debug("CSV row skipped: %s", e)
            skipped += 1

    return {
        "success":  True,
        "imported": imported,
        "skipped":  skipped,
        "message":  f"Imported {imported} transactions ({skipped} skipped).",
    }


def _normalise_date(raw: str) -> str:
    """Best-effort conversion of various date strings to YYYY-MM-DD."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y",
                "%d %b %Y", "%d-%b-%Y", "%d %B %Y"):
        try:
            return datetime.datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.date.today().isoformat()


# ===========================================================================
# Spending summary / analytics
# ===========================================================================

def get_spending_summary() -> dict:
    """
    Reshape backend analyzer output into the richer structure the
    frontend dashboard and charts expect.

    Output keys:
        total_spending, monthly_spending, by_category,
        monthly_trend, daily_spending, top_category, transaction_count
    """
    from backend.expenses.analyzer import analyze_spending
    from backend.database import get_expenses

    try:
        # ── All-time totals ───────────────────────────────────────
        all_analysis = analyze_spending(user_id=_get_user_id())
        all_expenses = get_expenses(limit=10_000, user_id=_get_user_id())

        if not all_expenses:
            return _empty_summary()

        # ── Monthly spending (current month) ──────────────────────
        this_month   = datetime.date.today().strftime("%Y-%m")
        start_month  = f"{this_month}-01"
        end_month    = datetime.date.today().isoformat()
        monthly_total = sum(
            e["amount"] for e in all_expenses
            if str(e.get("date", "")).startswith(this_month)
        )

        # ── Category totals (all time, frontend names) ────────────
        raw_by_cat   = all_analysis.get("by_category", {})
        by_cat_front: dict[str, float] = {}
        for backend_cat, amt in raw_by_cat.items():
            front_cat = _to_frontend_cat(backend_cat)
            by_cat_front[front_cat] = round(
                by_cat_front.get(front_cat, 0) + amt, 2
            )

        top_cat = (
            max(by_cat_front, key=by_cat_front.get)
            if by_cat_front else "N/A"
        )

        # ── Monthly trend (last 12 months) ───────────────────────
        monthly_map: dict[str, float] = {}
        for e in all_expenses:
            m = str(e.get("date", ""))[:7]
            if m:
                monthly_map[m] = round(monthly_map.get(m, 0) + e["amount"], 2)
        monthly_trend = [
            {"month": m, "amount": a}
            for m, a in sorted(monthly_map.items())[-12:]
        ]

        # ── Daily spending (last 60 days) ─────────────────────────
        daily_map: dict[str, float] = {}
        for e in all_expenses:
            d = str(e.get("date", ""))[:10]
            if d:
                daily_map[d] = round(daily_map.get(d, 0) + e["amount"], 2)
        daily_spending = [
            {"date": d, "amount": a}
            for d, a in sorted(daily_map.items())[-60:]
        ]

        return {
            "total_spending":    round(all_analysis["summary"]["total"], 2),
            "monthly_spending":  round(monthly_total, 2),
            "by_category":       by_cat_front,
            "monthly_trend":     monthly_trend,
            "daily_spending":    daily_spending,
            "top_category":      top_cat,
            "transaction_count": len(all_expenses),
        }

    except Exception as e:
        logger.error("get_spending_summary failed: %s", e)
        return _empty_summary()


def _empty_summary() -> dict:
    return {
        "total_spending": 0, "monthly_spending": 0,
        "by_category": {}, "monthly_trend": [],
        "daily_spending": [], "top_category": "N/A",
        "transaction_count": 0,
    }


# ===========================================================================
# Budget
# ===========================================================================

def get_budget_settings() -> dict:
    """
    Output: {income: float, budgets: {frontend_category: amount}}
    """
    from backend.budgeting.budget_engine import get_budget_settings as _get
    try:
        raw = _get(user_id=_get_user_id())
        front_budgets: dict[str, float] = {}
        for backend_cat, amt in raw.get("budgets", {}).items():
            front_cat = _to_frontend_cat(backend_cat)
            front_budgets[front_cat] = round(
                front_budgets.get(front_cat, 0) + amt, 2
            )
        full = {cat: front_budgets.get(cat, 0.0) for cat in CATEGORIES}
        return {"income": raw.get("income", 0.0), "budgets": full}
    except Exception as e:
        logger.error("get_budget_settings failed: %s", e)
        return {"income": 0.0, "budgets": {cat: 0.0 for cat in CATEGORIES}}


def save_budget_settings(income: float, budgets: dict) -> dict:
    """
    Input : income, {frontend_category: amount}
    Output: {success, message}
    """
    from backend.budgeting.budget_engine import save_budget_settings as _save
    try:
        backend_budgets = {
            _to_backend_cat(cat): amt
            for cat, amt in budgets.items()
            if amt > 0
        }
        return _save(income, backend_budgets, user_id=_get_user_id())
    except Exception as e:
        logger.error("save_budget_settings failed: %s", e)
        return {"success": False, "message": str(e)}


def calculate_budget() -> dict:
    """
    Calls backend calculate_budget and translates categories to frontend names.
    """
    from backend.budgeting.budget_engine import calculate_budget as _calc
    try:
        raw = _calc(user_id=_get_user_id())
        translated_rows = []
        merged: dict[str, dict] = {}

        for row in raw.get("by_category", []):
            front = _to_frontend_cat(row["category"])
            if front not in merged:
                merged[front] = {
                    "category":   front,
                    "budget":     0.0,
                    "spent":      0.0,
                    "remaining":  0.0,
                }
            merged[front]["budget"] += row["budget"]
            merged[front]["spent"]  += row["spent"]

        for m in merged.values():
            m["budget"]    = round(m["budget"], 2)
            m["spent"]     = round(m["spent"],  2)
            m["remaining"] = round(m["budget"] - m["spent"], 2)
            m["pct"]       = round(m["spent"] / m["budget"] * 100, 1) if m["budget"] > 0 else 0.0
            m["over_budget"] = m["spent"] > m["budget"] and m["budget"] > 0
            translated_rows.append(m)

        # Ensure every frontend category appears in the list
        present = {r["category"] for r in translated_rows}
        for cat in CATEGORIES:
            if cat not in present:
                translated_rows.append({
                    "category": cat, "budget": 0.0, "spent": 0.0,
                    "remaining": 0.0, "pct": 0.0, "over_budget": False,
                })

        return {
            "income":           raw.get("income", 0.0),
            "total_budget":     raw.get("total_budget", 0.0),
            "total_spent":      raw.get("total_spent",  0.0),
            "remaining":        raw.get("remaining",    0.0),
            "savings_estimate": raw.get("savings_estimate", 0.0),
            "by_category":      translated_rows,
        }
    except Exception as e:
        logger.error("calculate_budget failed: %s", e)
        return {
            "income": 0.0, "total_budget": 0.0, "total_spent": 0.0,
            "remaining": 0.0, "savings_estimate": 0.0, "by_category": [],
        }


# ===========================================================================
# Goals  (no backend module — session state only)
# ===========================================================================

# ===========================================================================
# Goals  (persisted per-user in DB)
# ===========================================================================

def get_goals() -> list[dict]:
    from backend.auth import get_goals as _get
    user_id = _get_user_id()
    if not user_id:
        return []
    return _get(user_id)


def save_goal(goal: dict) -> dict:
    from backend.auth import save_goal as _save
    user_id = _get_user_id()
    if not user_id:
        return {"success": False, "message": "Not logged in."}
    return _save(user_id, goal)


def update_goal(goal_id: int, updated: dict) -> dict:
    from backend.auth import update_goal as _upd
    user_id = _get_user_id()
    if not user_id:
        return {"success": False, "message": "Not logged in."}
    return _upd(goal_id, user_id, updated)


def delete_goal(goal_id: int) -> dict:
    from backend.auth import delete_goal as _del
    user_id = _get_user_id()
    if not user_id:
        return {"success": False, "message": "Not logged in."}
    return _del(goal_id, user_id)


# ===========================================================================
# AI Advisor
# ===========================================================================

def generate_financial_advice(summary: dict, guru: str = "General Financial Principles") -> dict:
    """
    Calls the real LLM advisor (Gemini/OpenAI) with fallback to offline templates.
    """
    from backend.advisor.advisor import generate_financial_advice as _advise
    try:
        return _advise(summary, guru)
    except Exception as e:
        logger.error("generate_financial_advice failed: %s", e)
        return {
            "observation":    "Could not generate advice at this time.",
            "recommendation": "Please check your API key configuration.",
            "why":            str(e),
            "action":         "Verify GOOGLE_API_KEY or OPENAI_API_KEY in your .env file.",
            "guru":           guru,
            "disclaimer":     "This is not financial advice.",
            "_mock":          True,
        }


# ===========================================================================
# Splitwise  (no backend module — demo data only)
# ===========================================================================

_MOCK_SPLITWISE: list[dict] = []


def get_splitwise_expenses() -> list[dict]:
    try:
        from backend.splitwise.splitwise_client import get_splitwise_expenses as _sw
        return _sw()
    except (ImportError, ModuleNotFoundError):
        return []


# ===========================================================================
# Utility
# ===========================================================================

def is_backend_available(module: str) -> bool:
    """Return True if a backend module is importable (used for status pills)."""
    try:
        import importlib
        importlib.import_module(module)
        return True
    except (ImportError, ModuleNotFoundError, Exception):
        return False
