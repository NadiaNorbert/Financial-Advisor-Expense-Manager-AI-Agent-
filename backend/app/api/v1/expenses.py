"""
backend/app/api/v1/expenses.py
==============================
Expense CRUD, search, filter, categorization, and CSV bulk import.
"""

from __future__ import annotations
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
import pandas as pd

from backend.app.schemas.all_schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseOut,
    CategorizeRequest,
    CategorizeResponse,
    BulkImportResponse,
)
from backend.app.core.security import get_current_user_optional, get_current_user
from backend.database import (
    add_expense as db_add_expense,
    get_expenses as db_get_expenses,
    get_expense_by_id as db_get_expense_by_id,
    update_expense as db_update_expense,
    delete_expense as db_delete_expense,
)
from backend.expenses.categorizer import categorize_expense, get_available_categories
from backend.adapter import (
    _to_backend_cat,
    _to_frontend_cat,
    _db_row_to_frontend,
    _normalise_date,
    CATEGORIES,
    PAYMENT_METHODS,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=List[ExpenseOut])
def list_expenses(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=1000, le=5000),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else None
    backend_cat = _to_backend_cat(category) if category and category != "All Categories" else None
    
    rows = db_get_expenses(
        category=backend_cat,
        start_date=start_date or None,
        end_date=end_date or None,
        limit=limit,
        user_id=user_id,
    )
    
    expenses = [_db_row_to_frontend(r) for r in rows]
    
    # In-memory search filter for merchant if provided
    if search:
        s = search.strip().lower()
        expenses = [e for e in expenses if s in e.get("merchant", "").lower()]
        
    return expenses


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else None
    backend_cat = _to_backend_cat(data.category)
    
    db_payload = {
        "merchant": data.merchant.strip(),
        "amount": round(float(data.amount), 2),
        "date": str(data.date),
        "category": backend_cat,
        "payment_method": data.payment or "Other",
        "source": data.source or "manual",
        "notes": data.notes or None,
    }
    
    try:
        new_id = db_add_expense(db_payload, user_id=user_id)
    except ValueError as e:
        msg = str(e)
        if "duplicate:" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg.replace("duplicate:", "").strip(),
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    row = db_get_expense_by_id(new_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch created expense")
    return _db_row_to_frontend(row)


@router.get("/categories", response_model=List[str])
def get_categories():
    return CATEGORIES


@router.get("/payment-methods", response_model=List[str])
def get_payment_methods():
    return PAYMENT_METHODS


@router.post("/categorize", response_model=CategorizeResponse)
def auto_categorize(data: CategorizeRequest):
    res = categorize_expense(data.merchant, data.description or "")
    front_cat = _to_frontend_cat(res["category"])
    return {"category": front_cat, "confidence": res["confidence"]}


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    row = db_get_expense_by_id(expense_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if current_user and row.get("user_id") and row["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _db_row_to_frontend(row)


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    row = db_get_expense_by_id(expense_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if current_user and row.get("user_id") and row["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    updates = {}
    if data.merchant is not None:
        updates["merchant"] = data.merchant.strip()
    if data.amount is not None:
        updates["amount"] = round(float(data.amount), 2)
    if data.date is not None:
        updates["date"] = str(data.date)
    if data.category is not None:
        updates["category"] = _to_backend_cat(data.category)
    if data.payment is not None:
        updates["payment_method"] = data.payment
    if data.notes is not None:
        updates["notes"] = data.notes
        
    ok = db_update_expense(expense_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Update failed")
    
    updated_row = db_get_expense_by_id(expense_id)
    return _db_row_to_frontend(updated_row)


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    row = db_get_expense_by_id(expense_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if current_user and row.get("user_id") and row["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    ok = db_delete_expense(expense_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delete failed")
    return {"success": True, "message": "Expense deleted successfully."}


@router.post("/import-csv", response_model=BulkImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else None
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid CSV file: {e}")
    
    if df.empty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded CSV file is empty.")
    
    imported = 0
    skipped = 0
    for _, r in df.iterrows():
        try:
            merchant = str(
                r.get("merchant") or r.get("Merchant") or
                r.get("description") or r.get("Description") or "Unknown"
            ).strip()
            raw_amt = r.get("amount") or r.get("Amount") or r.get("debit") or r.get("Debit") or 0
            amount = float(str(raw_amt).replace(",", ""))
            if amount <= 0 or merchant.lower() in ("", "unknown"):
                skipped += 1
                continue
            
            raw_date = str(r.get("date") or r.get("Date") or r.get("transaction_date") or "").strip()
            norm_date = _normalise_date(raw_date)
            
            frontend_cat = str(r.get("category") or r.get("Category") or "").strip()
            if not frontend_cat or frontend_cat not in CATEGORIES:
                frontend_cat = _to_frontend_cat(categorize_expense(merchant)["category"])
            backend_cat = _to_backend_cat(frontend_cat)
            
            payment = str(r.get("payment") or r.get("Payment") or r.get("payment_method") or "Other").strip()
            notes = str(r.get("notes") or r.get("Notes") or "").strip() or None
            
            db_add_expense({
                "merchant": merchant,
                "amount": round(amount, 2),
                "date": norm_date,
                "category": backend_cat,
                "payment_method": payment,
                "source": "csv",
                "notes": notes,
            }, user_id=user_id)
            imported += 1
        except Exception:
            skipped += 1
            
    return {
        "success": True,
        "imported": imported,
        "skipped": skipped,
        "message": f"Successfully imported {imported} transactions ({skipped} skipped).",
    }
