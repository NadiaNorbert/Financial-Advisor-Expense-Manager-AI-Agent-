# Expenses sub-package
"""Expenses sub-package – extraction, categorisation, analysis."""
from backend.expenses.extractor import extract_expense_from_text
from backend.expenses.categorizer import categorize_expense
from backend.expenses.analyzer import (
    get_spending_summary,
    get_category_summary,
    analyze_spending,
)

__all__ = [
    "extract_expense_from_text",
    "categorize_expense",
    "get_spending_summary",
    "get_category_summary",
    "analyze_spending",
]