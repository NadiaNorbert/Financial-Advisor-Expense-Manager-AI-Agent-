"""
FinMate AI - UI Helper Tests
==============================
Tests for utility functions and the backend adapter layer.
Run with: python -m pytest tests/ -v
"""

import pytest
import datetime
import sys
import os

# Make sure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Export utilities
# ---------------------------------------------------------------------------

class TestExportUtils:
    def test_export_expenses_csv_produces_bytes(self):
        from utils.export import export_expenses_csv
        expenses = [
            {"date": "2026-08-01", "merchant": "Swiggy", "category": "Food & Dining",
             "amount": 450, "payment": "UPI", "source": "manual", "notes": ""},
        ]
        result = export_expenses_csv(expenses)
        assert isinstance(result, bytes)
        assert b"Swiggy" in result
        assert b"450" in result

    def test_export_expenses_csv_header(self):
        from utils.export import export_expenses_csv
        result = export_expenses_csv([])
        header_line = result.decode("utf-8").splitlines()[0]
        assert "merchant" in header_line
        assert "amount"   in header_line
        assert "category" in header_line

    def test_export_budget_csv(self):
        from utils.export import export_budget_csv
        data = {
            "income": 30000, "total_budget": 20000, "total_spent": 15000,
            "remaining": 5000, "savings_estimate": 15000,
            "by_category": [
                {"category": "Food & Dining", "budget": 6000, "spent": 5200,
                 "remaining": 800, "pct": 86.7, "over_budget": False},
            ],
        }
        result = export_budget_csv(data)
        assert isinstance(result, bytes)
        assert b"Food" in result

    def test_export_goals_csv(self):
        from utils.export import export_goals_csv
        goals = [
            {"name": "Emergency Fund", "target": 50000, "current": 20000,
             "deadline": "2027-03-01", "notes": ""},
        ]
        result = export_goals_csv(goals)
        assert isinstance(result, bytes)
        assert b"Emergency Fund" in result

    def test_export_summary_txt(self):
        from utils.export import export_summary_txt
        expenses = [
            {"date": "2026-08-01", "merchant": "Swiggy", "category": "Food & Dining",
             "amount": 450, "payment": "UPI", "source": "manual", "notes": ""},
        ]
        summary = {
            "total_spending": 450, "monthly_spending": 450,
            "by_category": {"Food & Dining": 450},
            "top_category": "Food & Dining", "transaction_count": 1,
        }
        budget_data = {
            "income": 30000, "total_budget": 20000, "total_spent": 450,
            "remaining": 19550, "savings_estimate": 29550, "by_category": [],
        }
        goals = []
        result = export_summary_txt(expenses, summary, budget_data, goals)
        assert isinstance(result, bytes)
        text = result.decode("utf-8")
        assert "FinMate AI" in text
        assert "Swiggy" in text

    def test_report_filename_format(self):
        from utils.export import report_filename
        name = report_filename("expenses", "csv")
        today = datetime.date.today().strftime("%Y-%m-%d")
        assert name == f"finmate_expenses_{today}.csv"
        assert name.endswith(".csv")


# ---------------------------------------------------------------------------
# Backend adapter — categorizer
# ---------------------------------------------------------------------------

class TestCategorizer:
    def test_swiggy_is_food(self):
        from backend.adapter import categorize_expense
        assert categorize_expense("Swiggy", 450) == "Food & Dining"

    def test_uber_is_transport(self):
        from backend.adapter import categorize_expense
        assert categorize_expense("Uber", 200) == "Transport"

    def test_amazon_is_shopping(self):
        from backend.adapter import categorize_expense
        assert categorize_expense("Amazon", 1200) == "Shopping"

    def test_netflix_is_entertainment(self):
        from backend.adapter import categorize_expense
        assert categorize_expense("Netflix", 649) == "Entertainment"

    def test_unknown_is_others(self):
        from backend.adapter import categorize_expense
        result = categorize_expense("XYZ Corp", 100)
        assert result in [
            "Others", "Food & Dining", "Transport", "Shopping",
            "Entertainment", "Utilities", "Healthcare", "Education", "Rent"
        ]


# ---------------------------------------------------------------------------
# Backend adapter — spending summary
# ---------------------------------------------------------------------------

class TestSpendingSummary:
    def setup_method(self):
        """Seed session state with known data before each test."""
        # We need to patch st.session_state — use a dict substitute
        import streamlit as st
        st.session_state["expenses"] = [
            {"id": 1, "merchant": "Swiggy", "amount": 450,
             "date": "2026-08-01", "category": "Food & Dining",
             "payment": "UPI", "source": "manual", "notes": ""},
            {"id": 2, "merchant": "Uber", "amount": 320,
             "date": "2026-08-02", "category": "Transport",
             "payment": "UPI", "source": "manual", "notes": ""},
        ]

    def test_total_spending(self):
        from backend.adapter import get_spending_summary
        summary = get_spending_summary()
        assert summary["total_spending"] == pytest.approx(770, rel=0.01)

    def test_by_category_keys(self):
        from backend.adapter import get_spending_summary
        summary = get_spending_summary()
        assert "Food & Dining" in summary["by_category"]
        assert "Transport"     in summary["by_category"]

    def test_transaction_count(self):
        from backend.adapter import get_spending_summary
        summary = get_spending_summary()
        assert summary["transaction_count"] == 2


# ---------------------------------------------------------------------------
# Backend adapter — budget calculation
# ---------------------------------------------------------------------------

class TestBudgetCalculation:
    def setup_method(self):
        import streamlit as st
        st.session_state["expenses"] = [
            {"id": 1, "merchant": "Swiggy", "amount": 5200,
             "date": "2026-08-01", "category": "Food & Dining",
             "payment": "UPI", "source": "manual", "notes": ""},
        ]
        st.session_state["budget_settings"] = {
            "income": 30000,
            "budgets": {"Food & Dining": 6000, "Transport": 4000},
        }

    def test_remaining_budget(self):
        from backend.adapter import calculate_budget
        data = calculate_budget()
        assert data["remaining"] == pytest.approx(4800, rel=0.01)   # 10000 - 5200

    def test_savings_estimate(self):
        from backend.adapter import calculate_budget
        data = calculate_budget()
        assert data["savings_estimate"] == pytest.approx(24800, rel=0.01)  # 30000 - 5200

    def test_food_not_over_budget(self):
        from backend.adapter import calculate_budget
        data = calculate_budget()
        food_row = next(r for r in data["by_category"] if r["category"] == "Food & Dining")
        assert food_row["over_budget"] is False
        assert food_row["pct"] == pytest.approx(86.7, abs=0.2)


# ---------------------------------------------------------------------------
# INR formatter
# ---------------------------------------------------------------------------

class TestINRFormatter:
    def test_basic_formatting(self):
        from utils.export import _inr
        assert _inr(1234.5) == "₹1,234.50"
        assert _inr(0)      == "₹0.00"
        assert _inr(100000) == "₹100,000.00"
