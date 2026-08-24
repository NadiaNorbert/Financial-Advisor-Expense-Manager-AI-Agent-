"""
expense_ocr.py – OCR pipeline for payment screenshots
======================================================
Supports common Indian payment screenshots:
  UPI / Google Pay / PhonePe / Paytm / Bank SMS / Bank statement images.

Primary backend : Google Gemini Vision (if GOOGLE_API_KEY is configured)
Fallback backend: Tesseract OCR (if pytesseract + opencv are installed)

Public API
----------
    extract_expense_from_image(image_path: str | Path) -> dict
"""

from __future__ import annotations

import base64
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config import SUPPORTED_IMAGE_EXTENSIONS, TESSERACT_PATH

logger = logging.getLogger(__name__)

# ── Optional Tesseract path configuration ─────────────────────────────────────
try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageOps
    import cv2
    import numpy as np

    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False
    logger.warning(
        "pytesseract / Pillow / opencv not installed. "
        "Will attempt Gemini Vision OCR instead."
    )

# ── Check Gemini Vision availability ──────────────────────────────────────────
def _gemini_ocr_available() -> bool:
    try:
        from backend.config import GOOGLE_API_KEY, LLM_PROVIDER
        if not (bool(GOOGLE_API_KEY) and LLM_PROVIDER == "google"):
            return False
        # Also verify the google-genai package is actually installed
        import importlib
        importlib.import_module("google.genai")
        return True
    except Exception:
        return False

# NOTE: do not cache this at module level — config may not be loaded yet.
# It is evaluated lazily inside extract_expense_from_image instead.
_OCR_AVAILABLE = _TESSERACT_AVAILABLE  # Tesseract availability is safe to check at import


# ── Amount patterns ────────────────────────────────────────────────────────────
# Matches: ₹450, Rs.450, Rs 450, INR 450, 1,23,456.78, 450.00
_AMOUNT_PATTERNS = [
    r"(?:₹|Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    r"([0-9]{1,3}(?:,[0-9]{2,3})+(?:\.[0-9]{1,2})?)",
    r"(?:amount|amt|paid|total)[:\s]*([0-9,]+(?:\.[0-9]{1,2})?)",
    r"\b([0-9]+\.[0-9]{2})\b",
]

# ── Date patterns ─────────────────────────────────────────────────────────────
_DATE_PATTERNS = [
    r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b",   # DD-MM-YYYY or DD/MM/YYYY
    r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",   # YYYY-MM-DD
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",
    r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",
]

# ── Merchant keyword sets ─────────────────────────────────────────────────────
_MERCHANT_KEYWORDS = [
    "paid to", "payment to", "transferred to", "sent to",
    "merchant", "payee", "to:", "pay to",
]

# ── Payment method keywords ───────────────────────────────────────────────────
_PAYMENT_METHODS = {
    "upi": "UPI",
    "gpay": "UPI",
    "google pay": "UPI",
    "phonepe": "UPI",
    "phone pe": "UPI",
    "paytm": "UPI",
    "bhim": "UPI",
    "neft": "Net Banking",
    "rtgs": "Net Banking",
    "imps": "Net Banking",
    "net banking": "Net Banking",
    "netbanking": "Net Banking",
    "debit card": "Debit Card",
    "credit card": "Credit Card",
    "cash": "Cash",
    "wallet": "Wallet",
    "amazon pay": "Wallet",
    "mobikwik": "Wallet",
    "freecharge": "Wallet",
}


# ─────────────────────────────────────────────────────────────────────────────
# Image pre-processing
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess_image(image_path: str) -> "Image.Image":
    """Convert image to a form that Tesseract handles best.

    Steps: grayscale → denoise → threshold → scale-up if tiny.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"OpenCV could not open image: {image_path}")

    # Scale up small images
    h, w = img.shape[:2]
    if max(h, w) < 1000:
        scale = 1000 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    from PIL import Image as PILImage
    return PILImage.fromarray(thresh)


# ─────────────────────────────────────────────────────────────────────────────
# Field extractors
# ─────────────────────────────────────────────────────────────────────────────

def _extract_amount(text: str) -> Optional[float]:
    """Return the most likely transaction amount from OCR text."""
    candidates: list[float] = []

    for pattern in _AMOUNT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(1).replace(",", "")
            try:
                val = float(raw)
                if 1.0 <= val <= 10_000_000:   # sane INR range
                    candidates.append(val)
            except ValueError:
                continue

    if not candidates:
        return None

    # Prefer amounts appearing after a ₹ / Rs symbol (first pattern)
    for pattern in _AMOUNT_PATTERNS[:1]:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(1).replace(",", "")
            try:
                return float(raw)
            except ValueError:
                pass

    return candidates[0]


def _normalise_date(raw: str) -> Optional[str]:
    """Convert various date formats to YYYY-MM-DD."""
    formats = [
        "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d",
        "%d %b %Y", "%d %B %Y",
        "%d-%b-%Y", "%d %b, %Y",
    ]
    raw = raw.strip()
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _extract_date(text: str) -> Optional[str]:
    """Return the first valid date found in OCR text."""
    for pattern in _DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            normalised = _normalise_date(match.group(1))
            if normalised:
                return normalised
    return None


def _extract_merchant(text: str) -> Optional[str]:
    """Extract merchant/payee name using keyword anchors."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for keyword in _MERCHANT_KEYWORDS:
        for line in lines:
            if keyword.lower() in line.lower():
                # Remove the keyword and grab the remainder
                idx = line.lower().find(keyword.lower())
                remainder = line[idx + len(keyword):].strip(" :-")
                if remainder and len(remainder) > 1:
                    return remainder[:60]  # cap length

    # Fallback: look for lines that look like business names
    # (mixed-case, no digits, reasonable length)
    for line in lines:
        if 3 <= len(line) <= 50 and not re.search(r"\d{4,}", line):
            # Skip lines that are clearly labels or amounts
            if not any(
                kw in line.lower()
                for kw in ["amount", "date", "time", "status", "ref", "txn", "utr", "balance"]
            ):
                return line[:60]

    return None


def _extract_payment_method(text: str) -> Optional[str]:
    """Detect payment method from OCR text."""
    lowered = text.lower()
    for keyword, method in _PAYMENT_METHODS.items():
        if keyword in lowered:
            return method
    return None


def _extract_transaction_type(text: str) -> str:
    """Determine whether the transaction is a debit or credit."""
    lowered = text.lower()
    credit_signals = ["credited", "received", "credit", "cashback", "refund", "added"]
    debit_signals = ["debited", "paid", "sent", "debit", "payment", "transferred", "deducted"]

    credit_count = sum(1 for s in credit_signals if s in lowered)
    debit_count = sum(1 for s in debit_signals if s in lowered)

    if debit_count > credit_count:
        return "debit"
    if credit_count > debit_count:
        return "credit"
    return "unknown"


def _compute_confidence(result: dict) -> float:
    """Heuristic confidence: fraction of key fields that are non-null."""
    fields = ["merchant", "amount", "date", "payment_method"]
    found = sum(1 for f in fields if result.get(f) is not None)
    return round(found / len(fields), 2)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def extract_expense_from_image(image_path: str | Path) -> dict:
    """Extract structured expense data from a payment screenshot.

    Parameters
    ----------
    image_path:
        Absolute or relative path to a JPG / JPEG / PNG image.

    Returns
    -------
    dict
        Keys: ``merchant``, ``amount``, ``date``, ``transaction_type``,
        ``payment_method``, ``raw_text``, ``confidence``, ``error``.
        Any field that could not be detected is ``None``.

    Examples
    --------
    >>> result = extract_expense_from_image("screenshots/gpay_swiggy.png")
    >>> result["amount"]
    450.0
    >>> result["merchant"]
    'Swiggy'
    """
    image_path = Path(image_path)

    # ── Validation ─────────────────────────────────────────────────────────
    if not image_path.exists():
        return _error_result(f"File not found: {image_path}")

    if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        return _error_result(
            f"Unsupported file type '{image_path.suffix}'. "
            f"Supported: {SUPPORTED_IMAGE_EXTENSIONS}"
        )

    if not _OCR_AVAILABLE and not _gemini_ocr_available():
        return _error_result(
            "No OCR backend available. "
            "Either install pytesseract/opencv or set GOOGLE_API_KEY in .env."
        )

    # ── Try Gemini Vision first (no local install required) ────────────────
    if _gemini_ocr_available():
        try:
            result = _gemini_vision_ocr(image_path)
            return result
        except Exception as exc:
            logger.warning("Gemini Vision OCR failed: %s", exc)
            # Only fall through to Tesseract if the binary actually works
            if _TESSERACT_AVAILABLE:
                try:
                    pytesseract.get_tesseract_version()  # check binary is present
                except Exception:
                    return _error_result(f"Gemini Vision OCR failed: {exc}")

    # ── Tesseract fallback ─────────────────────────────────────────────────
    if not _TESSERACT_AVAILABLE:
        return _error_result(
            "No OCR backend available. "
            "Install pytesseract/opencv or set GOOGLE_API_KEY in .env."
        )

    return _tesseract_ocr(image_path)


def _gemini_vision_ocr(image_path: Path) -> dict:
    """Use Google Gemini Vision to extract expense fields from an image."""
    from google import genai
    from google.genai import types
    from backend.config import GOOGLE_API_KEY, GOOGLE_MODEL

    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Read image bytes
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Detect mime type
    suffix = image_path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    mime_type = mime_map.get(suffix, "image/jpeg")

    prompt = """You are an AI assistant that extracts expense information from Indian payment screenshots.

Analyze this payment screenshot and extract the following information.
Return ONLY a valid JSON object with these exact keys (use null for missing fields):

{
  "merchant": "merchant or vendor name (string or null)",
  "amount": 123.45,
  "date": "YYYY-MM-DD format (string or null)",
  "payment_method": "UPI / Credit Card / Debit Card / Net Banking / Cash / Wallet (string or null)",
  "transaction_type": "debit or credit (string)",
  "raw_text": "all visible text from the image"
}

Rules:
- amount must be a number (no currency symbols), or null
- date must be in YYYY-MM-DD format, or null
- transaction_type: use "debit" for payments/purchases, "credit" for received/refunds
- Do not include any explanation or markdown, just the JSON object."""

    response = client.models.generate_content(
        model=GOOGLE_MODEL,
        contents=[
            types.Part.from_bytes(data=image_data, mime_type=mime_type),
            prompt,
        ],
    )

    raw_response = response.text.strip()
    logger.debug("Gemini Vision raw response: %s", raw_response)

    # Strip markdown code fences if present
    raw_response = re.sub(r"^```(?:json)?\s*", "", raw_response)
    raw_response = re.sub(r"\s*```$", "", raw_response)

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse Gemini response as JSON: {raw_response}")

    # Normalise amount
    amount = data.get("amount")
    if amount is not None:
        try:
            amount = float(str(amount).replace(",", ""))
            if amount <= 0 or amount > 10_000_000:
                amount = None
        except (ValueError, TypeError):
            amount = None

    result = {
        "merchant":         data.get("merchant") or None,
        "amount":           amount,
        "date":             data.get("date") or None,
        "transaction_type": data.get("transaction_type") or "unknown",
        "payment_method":   data.get("payment_method") or None,
        "raw_text":         data.get("raw_text") or "",
        "confidence":       0.0,
        "error":            None,
    }
    result["confidence"] = _compute_confidence(result)
    logger.info(
        "Gemini Vision OCR – merchant=%s amount=%s confidence=%.2f",
        result["merchant"], result["amount"], result["confidence"],
    )
    return result


def _tesseract_ocr(image_path: Path) -> dict:
    """Run traditional Tesseract OCR pipeline."""
    # ── OCR ────────────────────────────────────────────────────────────────
    try:
        pil_image = _preprocess_image(str(image_path))
    except Exception as exc:
        return _error_result(f"Image pre-processing failed: {exc}")

    try:
        raw_text: str = pytesseract.image_to_string(
            pil_image,
            lang="eng",
            config="--psm 6 --oem 3",
        )
    except pytesseract.TesseractNotFoundError:
        return _error_result(
            "Tesseract is not installed or not found on PATH. "
            "Install from https://github.com/UB-Mannheim/tesseract/wiki "
            "and set TESSERACT_PATH in your .env file."
        )
    except Exception as exc:
        return _error_result(f"OCR engine error: {exc}")

    if not raw_text.strip():
        return _error_result("OCR returned empty text. Image may be unreadable.")

    logger.debug("Raw OCR text:\n%s", raw_text)

    # ── Field extraction ───────────────────────────────────────────────────
    result = {
        "merchant": _extract_merchant(raw_text),
        "amount": _extract_amount(raw_text),
        "date": _extract_date(raw_text),
        "transaction_type": _extract_transaction_type(raw_text),
        "payment_method": _extract_payment_method(raw_text),
        "raw_text": raw_text,
        "confidence": 0.0,
        "error": None,
    }

    result["confidence"] = _compute_confidence(result)
    logger.info(
        "Tesseract OCR complete – merchant=%s amount=%s confidence=%.2f",
        result["merchant"],
        result["amount"],
        result["confidence"],
    )
    return result


def parse_ocr_text(raw_text: str) -> dict:
    """Parse already-extracted OCR text without re-running Tesseract.

    Useful for testing or when OCR has been run externally.

    Parameters
    ----------
    raw_text:
        Plain text from any OCR source.

    Returns
    -------
    dict
        Same structure as :func:`extract_expense_from_image`.
    """
    if not raw_text.strip():
        return _error_result("Empty text provided.")

    result = {
        "merchant": _extract_merchant(raw_text),
        "amount": _extract_amount(raw_text),
        "date": _extract_date(raw_text),
        "transaction_type": _extract_transaction_type(raw_text),
        "payment_method": _extract_payment_method(raw_text),
        "raw_text": raw_text,
        "confidence": 0.0,
        "error": None,
    }
    result["confidence"] = _compute_confidence(result)
    return result


def _error_result(message: str) -> dict:
    """Return a safe error dict that mirrors the normal result shape."""
    logger.error("OCR error: %s", message)
    return {
        "merchant": None,
        "amount": None,
        "date": None,
        "transaction_type": None,
        "payment_method": None,
        "raw_text": "",
        "confidence": 0.0,
        "error": message,
    }
