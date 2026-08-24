"""
auth.py – User authentication layer
=====================================
Handles user registration, login, and session management.
Passwords are hashed with bcrypt – plain-text is never stored.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

import bcrypt

from backend.config import DATABASE_PATH

logger = logging.getLogger(__name__)


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema ────────────────────────────────────────────────────────────────────

def init_auth_tables() -> None:
    """Create users and goals tables if they don't exist."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                email      TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password   TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )
        # Add user_id to expenses if missing
        try:
            conn.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id)")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Add user_id to budgets if missing
        try:
            conn.execute("ALTER TABLE budgets ADD COLUMN user_id INTEGER REFERENCES users(id)")
        except sqlite3.OperationalError:
            pass

        # Goals table (per-user, persisted)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                name       TEXT    NOT NULL,
                target     REAL    NOT NULL,
                current    REAL    NOT NULL DEFAULT 0,
                deadline   TEXT,
                notes      TEXT,
                created_at TEXT    NOT NULL
            )
            """
        )
    logger.info("Auth tables initialised")


# ── User management ───────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> dict:
    """Create a new user account.

    Returns
    -------
    dict  {success, user_id, message}
    """
    if not username.strip():
        return {"success": False, "message": "Username cannot be empty."}
    if not email.strip() or "@" not in email:
        return {"success": False, "message": "Please enter a valid email address."}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    now = datetime.utcnow().isoformat()

    try:
        with _get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
                (username.strip(), email.strip().lower(), hashed, now),
            )
        return {"success": True, "user_id": cur.lastrowid, "message": "Account created!"}
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            return {"success": False, "message": f"Username '{username}' is already taken."}
        if "email" in msg:
            return {"success": False, "message": "An account with that email already exists."}
        return {"success": False, "message": "Registration failed. Please try again."}


def login_user(username: str, password: str) -> dict:
    """Verify credentials and return user info.

    Returns
    -------
    dict  {success, user_id, username, email, message}
    """
    if not username.strip() or not password:
        return {"success": False, "message": "Please enter both username and password."}

    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()

    if not row:
        return {"success": False, "message": "Invalid username or password."}

    if not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return {"success": False, "message": "Invalid username or password."}

    return {
        "success":  True,
        "user_id":  row["id"],
        "username": row["username"],
        "email":    row["email"],
        "message":  f"Welcome back, {row['username']}!",
    }


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Fetch a user record by id."""
    with _get_conn() as conn:
        row = conn.execute("SELECT id, username, email, created_at FROM users WHERE id = ?",
                           (user_id,)).fetchone()
    return dict(row) if row else None


def update_password(user_id: int, old_password: str, new_password: str) -> dict:
    """Change a user's password after verifying the old one."""
    with _get_conn() as conn:
        row = conn.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()

    if not row or not bcrypt.checkpw(old_password.encode(), row["password"].encode()):
        return {"success": False, "message": "Current password is incorrect."}

    if len(new_password) < 6:
        return {"success": False, "message": "New password must be at least 6 characters."}

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    with _get_conn() as conn:
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
    return {"success": True, "message": "Password updated successfully."}


# ── Goals (per-user DB persistence) ──────────────────────────────────────────

def get_goals(user_id: int) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def save_goal(user_id: int, goal: dict) -> dict:
    now = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO goals (user_id, name, target, current, deadline, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, goal["name"], goal["target"], goal.get("current", 0),
             goal.get("deadline"), goal.get("notes"), now),
        )
    return {"success": True, "id": cur.lastrowid, "message": "Goal saved."}


def update_goal(goal_id: int, user_id: int, updated: dict) -> dict:
    allowed = {"name", "target", "current", "deadline", "notes"}
    safe = {k: v for k, v in updated.items() if k in allowed}
    if not safe:
        return {"success": False, "message": "No valid fields to update."}
    set_clause = ", ".join(f"{k} = ?" for k in safe)
    values = list(safe.values()) + [goal_id, user_id]
    with _get_conn() as conn:
        cur = conn.execute(
            f"UPDATE goals SET {set_clause} WHERE id = ? AND user_id = ?", values
        )
    return {"success": cur.rowcount > 0, "message": "Goal updated." if cur.rowcount else "Not found."}


def delete_goal(goal_id: int, user_id: int) -> dict:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id)
        )
    return {"success": cur.rowcount > 0, "message": "Goal deleted." if cur.rowcount else "Not found."}


# Bootstrap on import
init_auth_tables()
