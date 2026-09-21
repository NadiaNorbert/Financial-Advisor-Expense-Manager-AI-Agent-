"""
backend/app/schemas/all_schemas.py
==================================
Pydantic v2 schemas for all API requests and responses.
"""

from __future__ import annotations
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ── Auth Schemas ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


# ── Expense Schemas ──────────────────────────────────────────────────────────

class ExpenseBase(BaseModel):
    merchant: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    date: str = Field(..., description="YYYY-MM-DD")
    category: str = Field(default="Others")
    payment: Optional[str] = Field(default="Other")
    notes: Optional[str] = None
    source: Optional[str] = Field(default="manual")


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = None
    category: Optional[str] = None
    payment: Optional[str] = None
    notes: Optional[str] = None


class ExpenseOut(ExpenseBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[str] = None


class CategorizeRequest(BaseModel):
    merchant: str
    description: Optional[str] = ""
    amount: Optional[float] = 0.0


class CategorizeResponse(BaseModel):
    category: str
    confidence: float


class BulkImportResponse(BaseModel):
    success: bool
    imported: int
    skipped: int
    message: str


# ── Budget Schemas ───────────────────────────────────────────────────────────

class BudgetSettingsIn(BaseModel):
    income: float = Field(..., ge=0)
    budgets: Dict[str, float] = Field(default_factory=dict)
    month: Optional[str] = None


class BudgetSettingsOut(BaseModel):
    income: float
    budgets: Dict[str, float]
    month: str


class CategoryBudgetRow(BaseModel):
    category: str
    budget: float
    spent: float
    remaining: float
    pct: float
    over_budget: bool


class BudgetCalculationOut(BaseModel):
    income: float
    total_budget: float
    total_spent: float
    remaining: float
    savings_estimate: float
    by_category: List[CategoryBudgetRow]
    month: str


# ── Goals Schemas ────────────────────────────────────────────────────────────

class GoalBase(BaseModel):
    name: str = Field(..., min_length=1)
    target: float = Field(..., gt=0)
    current: float = Field(default=0.0, ge=0)
    deadline: Optional[str] = None
    notes: Optional[str] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target: Optional[float] = Field(None, gt=0)
    current: Optional[float] = Field(None, ge=0)
    deadline: Optional[str] = None
    notes: Optional[str] = None


class GoalOut(GoalBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[str] = None


# ── Analytics Schemas ────────────────────────────────────────────────────────

class SpendingSummaryOut(BaseModel):
    total_spending: float
    monthly_spending: float
    by_category: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
    daily_spending: List[Dict[str, Any]]
    top_category: str
    transaction_count: int


# ── Advisor Schemas ──────────────────────────────────────────────────────────

class AdviceRequest(BaseModel):
    guru: str = "General Financial Principles"
    summary: Optional[Dict[str, Any]] = None


class AdviceResponse(BaseModel):
    observation: str
    recommendation: str
    why: str
    action: str
    guru: str
    disclaimer: str
    is_mock: bool = Field(default=False, alias="_mock")


# ── OCR Schemas ──────────────────────────────────────────────────────────────

class OCRResponse(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    transaction_type: Optional[str] = None
    payment_method: Optional[str] = None
    confidence: float = 0.0
    raw_text: Optional[str] = ""
    error: Optional[str] = None
    is_mock: bool = Field(default=False, alias="_mock")
