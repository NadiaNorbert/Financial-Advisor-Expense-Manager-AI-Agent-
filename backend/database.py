"""
database.py – SQLite persistence layer
=======================================
All database interactions are centralised here.
Uses the sqlite3 stdlib – no ORM required.
"""

from __future__ import annotations

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from backend.config import DATABASE_PATH
from backend.models import Expense

logger = logging.getLogger(__name__)


# ── Connection helper ─────────────────────────────────────────────────────────

@contextmanager
def _get_conn():
    """Yield a SQLite connection and auto-commit / rollback."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL") # safer concurrent writes
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema initialisation ─────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they do not already exist.

    Call this once at application startup.
    """
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant       TEXT    NOT NULL,
                amount         REAL    NOT NULL CHECK (amount > 0),
                date           TEXT    NOT NULL,
                category       TEXT    NOT NULL DEFAULT 'Others',
                payment_method TEXT,
                source         TEXT,
                notes          TEXT,
                created_at     TEXT    NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_date
            ON expenses (date)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_category
            ON expenses (category)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                month      TEXT    NOT NULL,
                income     REAL    NOT NULL,
                category   TEXT    NOT NULL,
                budget_amt REAL    NOT NULL,
                created_at TEXT    NOT NULL,
                UNIQUE(month, category)
            )
            """
        )
    logger.info("Database initialised at %s", DATABASE_PATH)


# ── CRUD: Expenses ────────────────────────────────────────────────────────────

def add_expense(expense: Expense | dict, user_id: int | None = None) -> int:
    """Insert a new expense row, rejecting exact duplicates.

    Duplicate = same user, merchant, amount, and date already exists.

    Returns
    -------
    int
        The ``id`` of the newly inserted row.

    Raises
    ------
    ValueError
        If an identical expense already exists for this user.
    """
    if isinstance(expense, dict):
        expense = Expense(**expense)

    # ── Duplicate guard ───────────────────────────────────────────────────
    with _get_conn() as conn:
        existing = conn.execute(
            """
            SELECT id FROM expenses
            WHERE merchant = :merchant
              AND amount   = :amount
              AND date     = :date
              AND (user_id = :user_id OR (:user_id IS NULL AND user_id IS NULL))
            LIMIT 1
            """,
            {
                "merchant": expense.merchant,
                "amount":   expense.amount,
                "date":     expense.date,
                "user_id":  user_id,
            },
        ).fetchone()

    if existing:
        raise ValueError(
            f"duplicate:Expense already exists (ID #{existing['id']}): "
            f"{expense.merchant} ₹{expense.amount} on {expense.date}"
        )

    now = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO expenses
                (merchant, amount, date, category, payment_method, source, notes, created_at, user_id)
            VALUES
                (:merchant, :amount, :date, :category, :payment_method, :source, :notes, :created_at, :user_id)
            """,
            {
                "merchant": expense.merchant,
                "amount": expense.amount,
                "date": expense.date,
                "category": expense.category,
                "payment_method": expense.payment_method,
                "source": expense.source,
                "notes": expense.notes,
                "created_at": now,
                "user_id": user_id,
            },
        )
    logger.debug("Added expense id=%s merchant=%s user_id=%s", cur.lastrowid, expense.merchant, user_id)
    return cur.lastrowid


def update_expense(expense_id: int, updates: dict) -> bool:
    """Update one or more fields of an existing expense.

    Parameters
    ----------
    expense_id:
        Row id to update.
    updates:
        Dict of column → new value.  Only whitelisted columns are accepted.

    Returns
    -------
    bool
        ``True`` if a row was modified.
    """
    allowed = {
        "merchant", "amount", "date", "category",
        "payment_method", "source", "notes",
    }
    safe = {k: v for k, v in updates.items() if k in allowed}
    if not safe:
        logger.warning("update_expense: no valid fields provided")
        return False

    set_clause = ", ".join(f"{k} = :{k}" for k in safe)
    safe["expense_id"] = expense_id
    with _get_conn() as conn:
        cur = conn.execute(
            f"UPDATE expenses SET {set_clause} WHERE id = :expense_id",
            safe,
        )
    updated = cur.rowcount > 0
    logger.debug("update_expense id=%s updated=%s", expense_id, updated)
    return updated


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by id.

    Returns
    -------
    bool
        ``True`` if the row was found and deleted.
    """
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    deleted = cur.rowcount > 0
    logger.debug("delete_expense id=%s deleted=%s", expense_id, deleted)
    return deleted


def get_expenses(
    *,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500,
    user_id: int | None = None,
) -> list[dict]:
    """Retrieve expenses with optional filters.

    Parameters
    ----------
    category:
        Filter to a single expense category.
    start_date / end_date:
        Inclusive date range in ``YYYY-MM-DD`` format.
    limit:
        Maximum number of rows to return (default 500).
    user_id:
        When provided, only return expenses belonging to this user.

    Returns
    -------
    list[dict]
        Each dict represents one expense row.
    """
    clauses: list[str] = []
    params: dict = {}

    if user_id is not None:
        clauses.append("user_id = :user_id")
        params["user_id"] = user_id
    if category:
        clauses.append("category = :category")
        params["category"] = category
    if start_date:
        clauses.append("date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("date <= :end_date")
        params["end_date"] = end_date

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params["limit"] = limit

    with _get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM expenses {where} ORDER BY date DESC LIMIT :limit",
            params,
        ).fetchall()

    return [dict(r) for r in rows]


def get_expense_by_id(expense_id: int) -> Optional[dict]:
    """Fetch a single expense by its primary key."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    return dict(row) if row else None


def get_total_spending(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: int | None = None,
) -> float:
    """Return the sum of all expense amounts in the given date range."""
    clauses, params = [], {}
    if user_id is not None:
        clauses.append("user_id = :user_id")
        params["user_id"] = user_id
    if start_date:
        clauses.append("date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("date <= :end_date")
        params["end_date"] = end_date
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    with _get_conn() as conn:
        row = conn.execute(
            f"SELECT COALESCE(SUM(amount), 0) AS total FROM expenses {where}",
            params,
        ).fetchone()
    return round(float(row["total"]), 2)


def get_category_totals(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: int | None = None,
) -> dict[str, float]:
    """Return {category: total_amount} for the date range."""
    clauses, params = [], {}
    if user_id is not None:
        clauses.append("user_id = :user_id")
        params["user_id"] = user_id
    if start_date:
        clauses.append("date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("date <= :end_date")
        params["end_date"] = end_date
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    with _get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT category, COALESCE(SUM(amount), 0) AS total
            FROM expenses {where}
            GROUP BY category
            ORDER BY total DESC
            """,
            params,
        ).fetchall()
    return {r["category"]: round(float(r["total"]), 2) for r in rows}


# ── Budget persistence ─────────────────────────────────────────────────────────

def save_budget(month: str, income: float, category_budgets: dict[str, float],
                user_id: int | None = None) -> None:
    """Upsert budget allocations for a given month."""
    now = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        for cat, amt in category_budgets.items():
            conn.execute(
                """
                INSERT INTO budgets (month, income, category, budget_amt, created_at, user_id)
                VALUES (:month, :income, :category, :budget_amt, :created_at, :user_id)
                ON CONFLICT(month, category) DO UPDATE SET
                    income     = excluded.income,
                    budget_amt = excluded.budget_amt,
                    created_at = excluded.created_at
                """,
                {
                    "month": month,
                    "income": income,
                    "category": cat,
                    "budget_amt": amt,
                    "created_at": now,
                    "user_id": user_id,
                },
            )
    logger.debug("Saved budget for %s user_id=%s", month, user_id)


def get_budget(month: str, user_id: int | None = None) -> dict:
    """Retrieve saved budget for a month.

    Returns
    -------
    dict
        ``{"income": float, "categories": {category: budget_amt}}``
        or an empty dict if no budget is saved.
    """
    with _get_conn() as conn:
        if user_id is not None:
            rows = conn.execute(
                "SELECT * FROM budgets WHERE month = ? AND user_id = ?", (month, user_id)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM budgets WHERE month = ?", (month,)
            ).fetchall()

    if not rows:
        return {}

    income = float(rows[0]["income"])
    categories = {r["category"]: float(r["budget_amt"]) for r in rows}
    return {"income": income, "categories": categories}


# ── Bootstrap ─────────────────────────────────────────────────────────────────

# Auto-initialise on import so callers don't have to remember to call init_db()
init_db()
