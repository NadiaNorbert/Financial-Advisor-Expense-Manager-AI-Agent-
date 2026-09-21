"""
backend/app/api/v1/advisor.py
=============================
AI Financial Advisor endpoint with guru selector and structured financial advice.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends

from backend.app.schemas.all_schemas import (
    AdviceRequest,
    AdviceResponse,
)
from backend.app.core.security import get_current_user_optional
from backend.advisor.advisor import generate_financial_advice
from backend.adapter import get_spending_summary, get_budget_settings, GURU_PROMPTS

router = APIRouter(prefix="/advisor", tags=["AI Advisor"])

GURUS_LIST = [
    {
        "id": "General Financial Principles",
        "name": "General Financial Principles",
        "emoji": "📚",
        "tagline": "Universal money rules — save, budget, invest.",
        "color": "#14B8A6",
    },
    {
        "id": "Warren Buffett",
        "name": "Warren Buffett",
        "emoji": "💼",
        "tagline": "Value investing & long-term compounding.",
        "color": "#F59E0B",
    },
    {
        "id": "Robert Kiyosaki",
        "name": "Robert Kiyosaki",
        "emoji": "🏠",
        "tagline": "Assets vs liabilities & passive income.",
        "color": "#8B5CF6",
    },
    {
        "id": "Ramit Sethi",
        "name": "Ramit Sethi",
        "emoji": "🚀",
        "tagline": "Automation, guilt-free spending & big wins.",
        "color": "#3B82F6",
    },
]


@router.get("/gurus")
def get_gurus():
    return GURUS_LIST


@router.post("/generate", response_model=AdviceResponse)
def generate_advice(
    data: AdviceRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    # Fetch summary if not provided in payload
    summary = data.summary
    if not summary:
        summary = get_spending_summary()
        settings = get_budget_settings()
        if settings.get("income"):
            summary["income"] = settings["income"]
            
    advice_dict = generate_financial_advice(summary, data.guru)
    
    return AdviceResponse(
        observation=advice_dict.get("observation", "No observation available."),
        recommendation=advice_dict.get("recommendation", "No recommendation available."),
        why=advice_dict.get("why", "No reason provided."),
        action=advice_dict.get("action", "No action suggested."),
        guru=advice_dict.get("guru", data.guru),
        disclaimer=advice_dict.get(
            "disclaimer",
            "This is general educational information only and does NOT constitute certified financial advice.",
        ),
        _mock=advice_dict.get("_mock", False),
    )
