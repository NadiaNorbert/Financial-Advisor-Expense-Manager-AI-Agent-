"""
extractor.py – Turn raw OCR / text into a validated Expense object
===================================================================
Bridges the OCR output and the database model.

Public API
----------
    extract_expense_from_text(raw_text: str, source: str = "ocr") -> dict
    build_expense_from_ocr(ocr_result: dict) -> dict
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from backend.expenses.categorizer import categorize_expense
from backend.models import Expense
from backend.ocr.expense_ocr import parse_ocr_text

logger = logging.getLogger(__name__)


def extract_expense_from_text(
    raw_text: str,
    source: str = "ocr",
) -> dict:
    """Parse raw text and return a ready-to-save expense dict.

    Parameters
    ----------
    raw_text:
        OCR output or any free-form payment description.
    source:
        Where the text came from ('ocr', 'manual', 'csv').

    Returns
    -------
    dict
        Contains all :class:`~backend.models.Expense` fields plus
        ``"error"`` (``None`` on success).
    """
    ocr_result = parse_ocr_text(raw_text)
    return build_expense_from_ocr(ocr_result, source=source)


def build_expense_from_ocr(
    ocr_result: dict,
    source: str = "ocr",
    manual_category: Optional[str] = None,
) -> dict:
    """Convert an OCR result dict into a validated expense dict.

    Parameters
    ----------
    ocr_result:
        Dict returned by :func:`~backend.ocr.expense_ocr.extract_expense_from_image`
        or :func:`~backend.ocr.expense_ocr.parse_ocr_text`.
    source:
        Provenance label.
    manual_category:
        If supplied, skip auto-categorisation and use this category.

    Returns
    -------
    dict
        Validated expense dict or ``{"error": "..."}`` on failure.
    """
    if ocr_result.get("error"):
        return {"error": ocr_result["error"]}

    amount = ocr_result.get("amount")
    if amount is None:
        return {"error": "Could not extract a valid amount from the image/text."}

    merchant = ocr_result.get("merchant") or "Unknown Merchant"
    txn_date = ocr_result.get("date") or date.today().isoformat()

    # Auto-categorise unless a manual override is given
    if manual_category:
        category = manual_category
    else:
        cat_result = categorize_expense(
            merchant=merchant,
            description=ocr_result.get("raw_text", ""),
        )
        category = cat_result["category"]

    try:
        expense = Expense(
            merchant=merchant,
            amount=amount,
            date=txn_date,
            category=category,
            payment_method=ocr_result.get("payment_method"),
            source=source,
            notes=f"OCR confidence: {ocr_result.get('confidence', 0):.0%}",
        )
        return expense.model_dump()
    except Exception as exc:
        logger.error("Expense validation failed: %s", exc)
        return {"error": str(exc)}
