"""
pdf_processor.py – Extract expense data from financial PDFs
============================================================
Supports bank statements and invoices in PDF format.

Public API
----------
    process_financial_pdf(pdf_path: str | Path) -> dict
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from backend.config import SUPPORTED_PDF_EXTENSIONS
from backend.expenses.categorizer import categorize_expense

logger = logging.getLogger(__name__)


def _extract_text_pymupdf(pdf_path: str) -> str:
    """Extract raw text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages)
    except Exception as exc:
        logger.error("PyMuPDF extraction failed: %s", exc)
        return ""


def _extract_text_pypdf2(pdf_path: str) -> str:
    """Fallback extraction using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
    except Exception as exc:
        logger.error("PyPDF2 extraction failed: %s", exc)
        return ""


def _parse_transactions(text: str) -> list[dict]:
    """Heuristically parse debit transactions from bank statement text."""
    transactions = []

    # Pattern: date  description  amount (debit)
    # Handles common Indian bank statement formats
    patterns = [
        # DD/MM/YYYY or DD-MM-YYYY  description  amount
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+([A-Za-z0-9 /&\-\.]{5,50}?)\s+"
        r"(?:Dr\.?|Debit|DR)?\s*([\d,]+(?:\.\d{1,2})?)",
        # amount with ₹ symbol
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+([A-Za-z0-9 /&\-\.]{5,50}?)\s+"
        r"₹\s*([\d,]+(?:\.\d{1,2})?)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            raw_date, description, raw_amount = match.groups()
            try:
                amount = float(raw_amount.replace(",", ""))
                if amount <= 0:
                    continue
            except ValueError:
                continue

            # Normalise date to YYYY-MM-DD
            for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                try:
                    from datetime import datetime
                    norm_date = datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    norm_date = None

            if not norm_date:
                continue

            description = description.strip()
            cat_result = categorize_expense(description)

            transactions.append({
                "merchant": description,
                "amount": round(amount, 2),
                "date": norm_date,
                "category": cat_result["category"],
                "payment_method": "Net Banking",
                "source": "pdf",
                "notes": None,
            })

    return transactions


def process_financial_pdf(pdf_path: "str | Path") -> dict:
    """Extract and parse transactions from a financial PDF.

    Parameters
    ----------
    pdf_path:
        Path to a bank statement or invoice PDF.

    Returns
    -------
    dict
        Keys: ``transactions`` (list of expense dicts), ``raw_text``,
        ``page_count``, ``error`` (None on success).
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        return {"transactions": [], "raw_text": "", "page_count": 0,
                "error": f"File not found: {pdf_path}"}

    if pdf_path.suffix.lower() not in SUPPORTED_PDF_EXTENSIONS:
        return {"transactions": [], "raw_text": "", "page_count": 0,
                "error": f"Unsupported file type: {pdf_path.suffix}"}

    # Try PyMuPDF first, fall back to PyPDF2
    raw_text = _extract_text_pymupdf(str(pdf_path))
    if not raw_text.strip():
        logger.info("PyMuPDF returned empty text, trying PyPDF2…")
        raw_text = _extract_text_pypdf2(str(pdf_path))

    if not raw_text.strip():
        return {"transactions": [], "raw_text": "", "page_count": 0,
                "error": "Could not extract text from the PDF."}

    # Estimate page count
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        doc.close()
    except Exception:
        page_count = raw_text.count("\f") + 1

    transactions = _parse_transactions(raw_text)
    logger.info(
        "process_financial_pdf: found %d transactions in %s",
        len(transactions), pdf_path.name,
    )

    return {
        "transactions": transactions,
        "raw_text": raw_text,
        "page_count": page_count,
        "error": None,
    }
