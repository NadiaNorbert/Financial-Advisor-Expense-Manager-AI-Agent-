"""
models.py – Pydantic data models
=================================
All shared data structures live here so every module uses the same schema.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.config import EXPENSE_CATEGORIES


# ── OCR / Extraction ──────────────────────────────────────────────────────────

class OCRResult(BaseModel):
    """Raw result returned by the OCR pipeline."""

    merchant: Optional[str] = Field(None, description="Merchant / payee name")
    amount: Optional[float] = Field(None, ge=0, description="Transaction amount in INR")
    date: Optional[str] = Field(None, description="Transaction date (YYYY-MM-DD)")
    transaction_type: Optional[str] = Field(
        None, description="credit / debit / unknown"
    )
    payment_method: Optional[str] = Field(
        None, description="UPI / Card / Net Banking / Cash / Unknown"
    )
    raw_text: str = Field("", description="Full OCR output for debugging")
    confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Overall extraction confidence [0-1]"
    )
    error: Optional[str] = Field(None, description="Non-null if extraction failed")


# ── Categorisation ────────────────────────────────────────────────────────────

class CategoryResult(BaseModel):
    """Result of the expense categoriser."""

    category: str = Field(..., description="Expense category")
    confidence: float = Field(0.0, ge=0.0, le=1.0)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in EXPENSE_CATEGORIES:
            return "Others"
        return v


# ── Expense ───────────────────────────────────────────────────────────────────

class Expense(BaseModel):
    """A single expense record – mirrors the database row."""

    id: Optional[int] = None
    merchant: str = Field(..., min_length=1, description="Merchant name")
    amount: float = Field(..., gt=0, description="Amount in INR")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    category: str = Field(default="Others")
    payment_method: Optional[str] = None
    source: Optional[str] = Field(
        None, description="'ocr' | 'manual' | 'csv'"
    )
    notes: Optional[str] = None
    created_at: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Date '{v}' is not in YYYY-MM-DD format")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in EXPENSE_CATEGORIES:
            return "Others"
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)


# ── Budget ────────────────────────────────────────────────────────────────────

class CategoryBudget(BaseModel):
    """Budget allocation for a single expense category."""

    category: str
    budget: float = Field(..., gt=0)
    spent: float = Field(default=0.0, ge=0)

    @property
    def remaining(self) -> float:
        return round(self.budget - self.spent, 2)

    @property
    def utilization_pct(self) -> float:
        if self.budget == 0:
            return 0.0
        return round((self.spent / self.budget) * 100, 2)

    @property
    def status(self) -> str:
        if self.spent > self.budget:
            return "OVER_BUDGET"
        elif self.spent >= self.budget * 0.9:
            return "NEAR_LIMIT"
        return "ON_TRACK"


class BudgetSummary(BaseModel):
    """Full monthly budget summary."""

    month: str = Field(..., description="YYYY-MM")
    income: float = Field(..., gt=0)
    categories: list[CategoryBudget] = Field(default_factory=list)

    @property
    def total_budget(self) -> float:
        return round(sum(c.budget for c in self.categories), 2)

    @property
    def total_spent(self) -> float:
        return round(sum(c.spent for c in self.categories), 2)

    @property
    def total_remaining(self) -> float:
        return round(self.income - self.total_spent, 2)

    @property
    def savings_rate_pct(self) -> float:
        if self.income == 0:
            return 0.0
        return round(((self.income - self.total_spent) / self.income) * 100, 2)


# ── Advisor ───────────────────────────────────────────────────────────────────

class FinancialAdviceRequest(BaseModel):
    """Input for the financial advisor."""

    income: Optional[float] = Field(None, ge=0)
    expenses: list[dict] = Field(default_factory=list)
    category_summary: dict[str, float] = Field(default_factory=dict)
    budget_summary: Optional[dict] = None
    savings_goal: Optional[float] = None
    philosophy: str = Field(
        default="general",
        description="'warren_buffett' | 'robert_kiyosaki' | 'ramit_sethi' | 'general'",
    )
    user_question: Optional[str] = None


class FinancialAdviceResponse(BaseModel):
    """Output from the financial advisor."""

    advice: str
    disclaimer: str = (
        "⚠️  This is general educational information only and does NOT constitute "
        "certified financial advice. Please consult a SEBI-registered financial "
        "advisor before making any investment or financial decisions."
    )
    philosophy_used: str = "general"
    sources_used: list[str] = Field(default_factory=list)
