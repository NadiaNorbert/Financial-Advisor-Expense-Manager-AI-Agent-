"""
categorizer.py – Rule-based expense categorisation
====================================================
Uses keyword matching to assign an expense to one of the standard
Indian-context categories.  Designed to be fast, offline, and easy to extend.

Public API
----------
    categorize_expense(merchant: str, description: str = "") -> dict
    override_category(expense_id: int, new_category: str) -> bool
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from backend.config import EXPENSE_CATEGORIES

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Keyword mapping  (category → list of lowercase keywords / patterns)
# Add new merchants here to extend categorisation.
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Food": [
        "swiggy", "zomato", "dominos", "domino", "pizza hut", "mcdonalds",
        "mcdonald", "burger king", "kfc", "subway", "starbucks", "cafe",
        "restaurant", "biryani", "dhaba", "hotel", "food", "eat", "dine",
        "bakery", "chai", "canteen", "mess", "tiffin", "barbeque nation",
        "barbeque", "paradise", "haldirams", "haldiram", "udupi",
        "fasoos", "faasos", "box8", "freshmenu", "rebel foods",
    ],
    "Groceries": [
        "bigbasket", "big basket", "bb", "bb daily", "grofers", "blinkit", "zepto", "dunzo",
        "dmart", "d-mart", "more supermarket", "reliance fresh", "reliance smart",
        "spencer", "nature basket", "supermarket", "kirana", "provision",
        "grocery", "vegetables", "fruits", "milk", "dairy", "mother dairy",
        "amul", "aavin", "heritage", "sabzi",
    ],
    "Transport": [
        "uber", "ola", "rapido", "meru", "taxi", "cab", "auto", "rickshaw",
        "irctc", "railways", "indian railway", "train", "metro", "bus",
        "bmtc", "best bus", "dtc", "msrtc", "redbus", "abhibus",
        "petrol", "diesel", "fuel", "hp petrol", "iocl", "bharat petroleum",
        "indian oil", "shell", "parking", "fastag", "toll",
        "namma metro", "delhi metro", "mumbai metro",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho",
        "snapdeal", "paytm mall", "shopclues", "tatacliq", "tata cliq",
        "reliance digital", "croma", "vijay sales", "electronics",
        "fashion", "clothes", "clothing", "apparel", "shoes", "footwear",
        "puma", "nike", "adidas", "h&m", "zara", "westside", "pantaloons",
        "max fashion", "lifestyle", "shoppers stop", "central mall",
    ],
    "Entertainment": [
        "netflix", "amazon prime", "hotstar", "disney+", "zee5", "sony liv",
        "jio cinema", "bookmyshow", "pvr", "inox", "cinepolis",
        "spotify", "apple music", "youtube premium", "gaana",
        "gaming", "steam", "playstation", "xbox", "movie",
        "concert", "event", "show", "theatre", "cinema",
    ],
    "Bills": [
        "electricity", "electric bill", "bescom", "tata power", "msedcl",
        "bses", "adani electricity", "water bill", "bwssb",
        "broadband", "jio fiber", "airtel fiber", "act fibernet",
        "mobile recharge", "postpaid", "airtel", "jio", "vi", "vodafone",
        "bsnl", "idea", "recharge", "bill payment", "utility",
        "lic", "insurance premium", "bajaj allianz", "hdfc life",
    ],
    "Healthcare": [
        "apollo", "fortis", "max hospital", "manipal", "medanta",
        "hospital", "clinic", "doctor", "pharmacy", "medical",
        "medicine", "netmeds", "1mg", "pharmeasy", "practo",
        "lab", "pathology", "diagnostic", "test", "scan", "mri", "xray",
        "dental", "eye care", "opticals", "lenskart",
        "health insurance", "star health", "care health",
    ],
    "Education": [
        "school", "college", "university", "fees", "tuition",
        "byju", "unacademy", "vedantu", "coursera", "udemy",
        "books", "stationery", "pen", "notebook", "amazon books",
        "exam", "coaching", "classes", "institute",
    ],
    "Travel": [
        "makemytrip", "goibibo", "cleartrip", "yatra", "easemytrip",
        "flight", "indigo", "air india", "spicejet", "vistara",
        "akasa", "go air", "hotel", "oyo", "treebo", "fabhotels",
        "airbnb", "holiday", "trip", "tour", "visa",
    ],
    "Rent": [
        "rent", "house rent", "pg", "paying guest", "hostel",
        "flat rent", "apartment rent", "nobroker", "magicbricks",
    ],
    "Utilities": [
        "gas", "lpg", "indane", "hp gas", "bharat gas",
        "internet", "cable tv", "dth", "tata sky", "dish tv",
        "d2h", "airtel dth", "sun direct",
    ],
}


def categorize_expense(
    merchant: str,
    description: str = "",
    *,
    default_category: str = "Others",
) -> dict:
    """Categorise an expense using keyword matching.

    Parameters
    ----------
    merchant:
        Merchant / payee name.
    description:
        Additional text (e.g. raw OCR text, transaction notes).
    default_category:
        Fallback category if no keyword matches.

    Returns
    -------
    dict
        ``{"category": str, "confidence": float}``

    Examples
    --------
    >>> categorize_expense("Swiggy", "Food order")
    {'category': 'Food', 'confidence': 0.9}
    >>> categorize_expense("IRCTC Booking")
    {'category': 'Transport', 'confidence': 0.9}
    """
    combined = f"{merchant} {description}".lower()
    combined = re.sub(r"[^a-z0-9\s]", " ", combined)  # remove punctuation

    best_category = default_category
    best_score = 0
    total_keywords = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in combined:
                # Exact merchant name match is stronger than description match
                if keyword in merchant.lower():
                    score += 2
                else:
                    score += 1
        if score > best_score:
            best_score = score
            best_category = category
        total_keywords += len(keywords)

    # Confidence: full match on merchant name → 0.9, description only → 0.7
    if best_score >= 2:
        confidence = 0.9
    elif best_score == 1:
        confidence = 0.7
    else:
        confidence = 0.3  # fallback / Others

    result = {"category": best_category, "confidence": confidence}
    logger.debug(
        "categorize_expense merchant=%r → %s (conf=%.2f)",
        merchant, best_category, confidence,
    )
    return result


def override_category(expense_id: int, new_category: str) -> bool:
    """Manually override the category of a stored expense.

    Parameters
    ----------
    expense_id:
        Database row id.
    new_category:
        Must be one of the defined :data:`~backend.config.EXPENSE_CATEGORIES`.

    Returns
    -------
    bool
        ``True`` if the update succeeded.
    """
    if new_category not in EXPENSE_CATEGORIES:
        logger.warning(
            "override_category: '%s' is not a valid category.", new_category
        )
        return False

    from backend.database import update_expense

    return update_expense(expense_id, {"category": new_category})


def get_available_categories() -> list[str]:
    """Return the list of all supported expense categories."""
    return list(EXPENSE_CATEGORIES)
