"""
FinMate AI - Export Utilities
==============================
Handles CSV, TXT, and (optional) PDF report generation.
All functions return bytes so Streamlit's st.download_button can use them directly.
"""

from __future__ import annotations

import csv
import io
import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inr(amount: float) -> str:
    """Format a number as INR string: ₹1,234.00"""
    return f"\u20b9{amount:,.2f}"


def _now_str() -> str:
    return datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")


def _today_str() -> str:
    return datetime.date.today().strftime("%d %b %Y")


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_expenses_csv(expenses: list[dict]) -> bytes:
    """
    Convert a list of expense dicts to a UTF-8 encoded CSV bytes object.
    Columns: Date, Merchant, Category, Amount (INR), Payment Method, Source, Notes
    """
    output = io.StringIO()
    fieldnames = ["date", "merchant", "category", "amount", "payment", "source", "notes"]
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for e in sorted(expenses, key=lambda x: str(x.get("date", "")), reverse=True):
        writer.writerow({
            "date":     e.get("date", ""),
            "merchant": e.get("merchant", ""),
            "category": e.get("category", ""),
            "amount":   e.get("amount", 0),
            "payment":  e.get("payment", ""),
            "source":   e.get("source", ""),
            "notes":    e.get("notes", ""),
        })
    return output.getvalue().encode("utf-8")


def export_budget_csv(budget_data: dict) -> bytes:
    """
    Convert budget calculation results to CSV bytes.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(["FinMate AI — Monthly Budget Report"])
    writer.writerow(["Generated", _today_str()])
    writer.writerow([])
    writer.writerow(["Monthly Income", budget_data.get("income", 0)])
    writer.writerow(["Total Budget",   budget_data.get("total_budget", 0)])
    writer.writerow(["Total Spent",    budget_data.get("total_spent", 0)])
    writer.writerow(["Remaining",      budget_data.get("remaining", 0)])
    writer.writerow(["Savings Est.",   budget_data.get("savings_estimate", 0)])
    writer.writerow([])
    writer.writerow(["Category", "Budget (INR)", "Spent (INR)", "Remaining (INR)", "Usage %", "Status"])

    for row in budget_data.get("by_category", []):
        status = "OVER BUDGET" if row.get("over_budget") else "OK"
        writer.writerow([
            row["category"],
            row["budget"],
            row["spent"],
            row["remaining"],
            f"{row['pct']}%",
            status,
        ])

    return output.getvalue().encode("utf-8")


def export_goals_csv(goals: list[dict]) -> bytes:
    """Convert goals list to CSV bytes."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["FinMate AI — Savings Goals Report"])
    writer.writerow(["Generated", _today_str()])
    writer.writerow([])
    writer.writerow(["Goal", "Target (INR)", "Current (INR)", "Progress %", "Deadline", "Notes"])
    for g in goals:
        target = g.get("target", 0)
        current = g.get("current", 0)
        pct = round(current / target * 100, 1) if target > 0 else 0
        writer.writerow([
            g.get("name", ""),
            target,
            current,
            f"{pct}%",
            g.get("deadline", ""),
            g.get("notes", ""),
        ])
    return output.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# Plain-text Report
# ---------------------------------------------------------------------------

def export_summary_txt(
    expenses: list[dict],
    summary: dict,
    budget_data: dict,
    goals: list[dict],
    advice: dict | None = None,
) -> bytes:
    """
    Generate a plain-text financial report as UTF-8 bytes.
    """
    lines: list[str] = []

    def hr(char: str = "─", width: int = 58) -> None:
        lines.append(char * width)

    def heading(text: str) -> None:
        lines.append("")
        hr("═")
        lines.append(f"  {text.upper()}")
        hr("═")

    def subheading(text: str) -> None:
        lines.append(f"\n  {text}")
        hr("─")

    # ---- Header ----
    lines.append("╔══════════════════════════════════════════════════════╗")
    lines.append("║         FinMate AI — Financial Summary Report        ║")
    lines.append("╚══════════════════════════════════════════════════════╝")
    lines.append(f"  Generated : {_now_str()}")
    lines.append(f"  Transactions: {summary.get('transaction_count', 0)}")

    # ---- Spending Overview ----
    heading("Spending Overview")
    lines.append(f"  Total Spending   : {_inr(summary.get('total_spending', 0))}")
    lines.append(f"  This Month       : {_inr(summary.get('monthly_spending', 0))}")
    lines.append(f"  Top Category     : {summary.get('top_category', 'N/A')}")

    # ---- Category Breakdown ----
    subheading("By Category")
    by_cat = summary.get("by_category", {})
    for cat, amt in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {cat:<22} {_inr(amt):>12}")

    # ---- Budget ----
    heading("Budget Status")
    lines.append(f"  Monthly Income   : {_inr(budget_data.get('income', 0))}")
    lines.append(f"  Total Budget     : {_inr(budget_data.get('total_budget', 0))}")
    lines.append(f"  Total Spent      : {_inr(budget_data.get('total_spent', 0))}")
    lines.append(f"  Remaining        : {_inr(budget_data.get('remaining', 0))}")
    lines.append(f"  Savings Estimate : {_inr(budget_data.get('savings_estimate', 0))}")

    subheading("Category Budgets")
    for row in budget_data.get("by_category", []):
        status = " ⚠ OVER" if row.get("over_budget") else "  OK"
        lines.append(
            f"  {row['category']:<22} "
            f"{_inr(row['spent']):>10} / {_inr(row['budget']):<12}"
            f"({row['pct']:>5}%)  {status}"
        )

    # ---- Goals ----
    heading("Savings Goals")
    for g in goals:
        target = g.get("target", 0)
        current = g.get("current", 0)
        pct = round(current / target * 100, 1) if target > 0 else 0
        bar_filled = int(pct / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        lines.append(f"\n  {g.get('name', 'Goal')}")
        lines.append(f"  [{bar}] {pct}%")
        lines.append(f"  {_inr(current)} of {_inr(target)}  |  Deadline: {g.get('deadline', 'N/A')}")

    # ---- AI Advice ----
    if advice:
        heading(f"AI Advice — {advice.get('guru', 'General')}")
        lines.append(f"  Observation  : {advice.get('observation', '')}")
        lines.append(f"  Recommendation: {advice.get('recommendation', '')}")
        lines.append(f"  Why?          : {advice.get('why', '')}")
        lines.append(f"  Action        : {advice.get('action', '')}")

    # ---- Top Transactions ----
    heading("Recent Transactions (Last 10)")
    sorted_exp = sorted(expenses, key=lambda x: str(x.get("date", "")), reverse=True)[:10]
    lines.append(f"  {'Date':<12} {'Merchant':<22} {'Category':<20} {'Amount':>10}")
    hr()
    for e in sorted_exp:
        lines.append(
            f"  {str(e.get('date','')):<12} "
            f"{str(e.get('merchant','')):<22} "
            f"{str(e.get('category','')):<20} "
            f"{_inr(e.get('amount', 0)):>10}"
        )

    # ---- Disclaimer ----
    lines.append("")
    hr()
    lines.append("  DISCLAIMER: This report is for personal tracking purposes only.")
    lines.append("  It does not constitute professional financial advice.")
    hr()

    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

def report_filename(prefix: str, ext: str) -> str:
    """Generate a dated filename like 'finmate_expenses_2026-08-21.csv'"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    return f"finmate_{prefix}_{today}.{ext}"
