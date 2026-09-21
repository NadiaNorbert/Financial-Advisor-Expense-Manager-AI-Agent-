"""
backend/app/api/v1/ocr.py
=========================
OCR endpoints for receipt and screenshot scanning.
"""

from __future__ import annotations
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.app.schemas.all_schemas import OCRResponse
from backend.ocr.expense_ocr import extract_expense_from_image, parse_ocr_text
from backend.expenses.categorizer import categorize_expense
from backend.adapter import _to_frontend_cat

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/upload", response_model=OCRResponse)
async def scan_receipt(file: UploadFile = File(...)):
    suffix = Path(file.filename or "receipt.png").suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png"]:
        suffix = ".png"
        
    temp_path = None
    try:
        content = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name
            
        result = extract_expense_from_image(temp_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
                
    # Suggest category if merchant found
    suggested_cat = None
    if result.get("merchant"):
        cat_res = categorize_expense(result["merchant"])
        suggested_cat = _to_frontend_cat(cat_res["category"])
        
    return OCRResponse(
        merchant=result.get("merchant"),
        amount=result.get("amount"),
        date=result.get("date"),
        transaction_type=result.get("transaction_type"),
        payment_method=result.get("payment_method"),
        confidence=result.get("confidence", 0.0),
        raw_text=result.get("raw_text", ""),
        error=result.get("error"),
        _mock=result.get("_mock", False),
    )
