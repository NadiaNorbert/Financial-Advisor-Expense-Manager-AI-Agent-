"""
tests/test_fastapi_endpoints.py
===============================
Integration tests for the new FastAPI REST endpoints.
"""

import pytest
from starlette.testclient import TestClient
from backend.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "finmate-ai-backend"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "FinMate AI API"
    assert "api_v1" in data


def test_categories_endpoint():
    response = client.get("/api/v1/expenses/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert "Food & Dining" in categories


def test_payment_methods_endpoint():
    response = client.get("/api/v1/expenses/payment-methods")
    assert response.status_code == 200
    methods = response.json()
    assert "UPI" in methods
    assert "Credit Card" in methods


def test_categorize_endpoint():
    response = client.post("/api/v1/expenses/categorize", json={"merchant": "Swiggy"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Food & Dining"
    assert data["confidence"] > 0.5


def test_budget_calculate_endpoint():
    response = client.get("/api/v1/budget/calculate")
    assert response.status_code == 200
    data = response.json()
    assert "income" in data
    assert "by_category" in data
    assert isinstance(data["by_category"], list)


def test_advisor_gurus_endpoint():
    response = client.get("/api/v1/advisor/gurus")
    assert response.status_code == 200
    gurus = response.json()
    assert len(gurus) >= 4
    guru_names = [g["name"] for g in gurus]
    assert "Warren Buffett" in guru_names
    assert "Robert Kiyosaki" in guru_names


def test_advisor_generate_endpoint():
    response = client.post("/api/v1/advisor/generate", json={
        "guru": "Warren Buffett",
        "summary": {
            "total_spending": 15000,
            "monthly_spending": 15000,
            "by_category": {"Food & Dining": 5000, "Shopping": 10000},
            "transaction_count": 5,
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "observation" in data
    assert "recommendation" in data
    assert "why" in data
    assert "action" in data
    assert data["guru"] == "Warren Buffett"


def test_analytics_summary_endpoint():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_spending" in data
    assert "by_category" in data
