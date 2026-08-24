# FinMate AI - Backend package (Member 1)
"""
Financial Research Advisor – Backend Package
============================================
Public re-exports for Member 2 (Streamlit frontend).

Quick-import example
--------------------
    from backend import (
        extract_expense_from_image,
        categorize_expense,
        add_expense,
        get_expenses,
        get_spending_summary,
        get_category_summary,
        analyze_spending,
        generate_financial_advice,
        calculate_budget,
        process_financial_pdf,
    )
"""

from backend.ocr.expense_ocr import extract_expense_from_image
from backend.expenses.extractor import extract_expense_from_text
from backend.expenses.categorizer import categorize_expense
from backend.expenses.analyzer import (
    get_spending_summary,
    get_category_summary,
    analyze_spending,
)
from backend.database import (
    add_expense,
    update_expense,
    delete_expense,
    get_expenses,
    init_db,
)
from backend.advisor.advisor import generate_financial_advice
from backend.budgeting.budget_engine import calculate_budget
from backend.documents.pdf_processor import process_financial_pdf

__all__ = [
    # OCR
    "extract_expense_from_image",
    # Text extraction
    "extract_expense_from_text",
    # Categorization
    "categorize_expense",
    # Database CRUD
    "add_expense",
    "update_expense",
    "delete_expense",
    "get_expenses",
    "init_db",
    # Analysis
    "get_spending_summary",
    "get_category_summary",
    "analyze_spending",
    # Advisor
    "generate_financial_advice",
    # Budgeting
    "calculate_budget",
    # Documents
    "process_financial_pdf",
]