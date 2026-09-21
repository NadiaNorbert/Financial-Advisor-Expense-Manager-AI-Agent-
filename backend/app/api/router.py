"""
backend/app/api/router.py
=========================
Aggregated API Router for FinMate AI v1 endpoints.
"""

from fastapi import APIRouter
from backend.app.api.v1 import (
    auth,
    expenses,
    budget,
    goals,
    analytics,
    advisor,
    ocr,
    reports,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(expenses.router)
api_router.include_router(budget.router)
api_router.include_router(goals.router)
api_router.include_router(analytics.router)
api_router.include_router(advisor.router)
api_router.include_router(ocr.router)
api_router.include_router(reports.router)
