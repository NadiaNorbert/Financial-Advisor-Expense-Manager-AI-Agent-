"""
main.py – Financial Research Advisor CLI
=========================================
Run with:
    python main.py
"""

from __future__ import annotations

import sys
from datetime import date, datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def _header(title: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def _pick(prompt: str, options: list[str]) -> str:
    """Show a numbered menu and return the chosen value."""
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input(f"{prompt} [1-{len(options)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  Invalid choice, try again.")


def _ask(prompt: str, default: str = "") -> str:
    val = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return val if val else default


def _ask_float(prompt: str) -> float:
    while True:
        raw = input(f"{prompt}: ").strip()
        try:
            val = float(raw.replace(",", ""))
            if val > 0:
                return val
        except ValueError:
            pass
        print("  Please enter a valid positive number.")


# ── Menu handlers ─────────────────────────────────────────────────────────────

def menu_add_expense() -> None:
    from backend.database import add_expense
    from backend.expenses.categorizer import categorize_expense, get_available_categories
    from backend.models import EXPENSE_CATEGORIES

    _header("Add Expense")

    merchant = _ask("Merchant / Payee name")
    if not merchant:
        print("  Merchant name cannot be empty.")
        return

    amount = _ask_float("Amount (₹)")

    today = date.today().isoformat()
    exp_date = _ask("Date (YYYY-MM-DD)", today)
    try:
        datetime.strptime(exp_date, "%Y-%m-%d")
    except ValueError:
        print("  Invalid date format. Using today.")
        exp_date = today

    # Auto-categorise then let user confirm / override
    auto = categorize_expense(merchant)
    print(f"\n  Auto-detected category: {auto['category']} (confidence {auto['confidence']:.0%})")
    change = _ask("  Use a different category? (y/N)", "n")
    if change.lower() == "y":
        category = _pick("  Choose category", get_available_categories())
    else:
        category = auto["category"]

    payment_methods = ["UPI", "Debit Card", "Credit Card", "Net Banking", "Cash", "Wallet", "Other"]
    payment_method = _pick("Payment method", payment_methods)

    notes = _ask("Notes (optional)", "")

    expense_id = add_expense({
        "merchant": merchant,
        "amount": amount,
        "date": exp_date,
        "category": category,
        "payment_method": payment_method,
        "source": "manual",
        "notes": notes or None,
    })
    print(f"\n  ✓ Expense saved (id={expense_id})")


def menu_scan_receipt() -> None:
    from backend.ocr.expense_ocr import extract_expense_from_image
    from backend.expenses.extractor import build_expense_from_ocr
    from backend.database import add_expense

    _header("Scan Receipt / Screenshot")

    print("  Enter the full path to your receipt/screenshot image.")
    path = input("  Path: ").strip().strip('"').strip("'")
    if not path:
        return

    print("  Running OCR…")
    ocr = extract_expense_from_image(path)

    if ocr.get("error"):
        print(f"  ✗ OCR failed: {ocr['error']}")
        return

    print(f"\n  OCR results:")
    print(f"    Merchant : {ocr.get('merchant', '–')}")
    print(f"    Amount   : ₹{ocr.get('amount', '–')}")
    print(f"    Date     : {ocr.get('date', '–')}")
    print(f"    Method   : {ocr.get('payment_method', '–')}")
    print(f"    Confidence: {ocr.get('confidence', 0):.0%}")

    save = _ask("\n  Save this expense? (Y/n)", "y")
    if save.lower() != "n":
        expense_dict = build_expense_from_ocr(ocr)
        if expense_dict.get("error"):
            print(f"  ✗ Could not build expense: {expense_dict['error']}")
            return
        expense_id = add_expense(expense_dict)
        print(f"  ✓ Expense saved (id={expense_id})")


def menu_view_expenses() -> None:
    from backend.database import get_expenses, get_category_totals, get_total_spending

    _header("View Expenses")

    start = _ask("Start date (YYYY-MM-DD, leave blank for all)", "")
    end = _ask("End date (YYYY-MM-DD, leave blank for all)", "")

    expenses = get_expenses(
        start_date=start or None,
        end_date=end or None,
        limit=50,
    )

    if not expenses:
        print("\n  No expenses found.")
        return

    print(f"\n  {'ID':<5} {'Date':<12} {'Merchant':<25} {'Category':<15} {'Amount':>10}")
    print(f"  {'─'*5} {'─'*12} {'─'*25} {'─'*15} {'─'*10}")
    for e in expenses:
        print(
            f"  {e['id']:<5} {e['date']:<12} {e['merchant'][:24]:<25} "
            f"{e['category']:<15} ₹{e['amount']:>9,.2f}"
        )

    total = get_total_spending(start or None, end or None)
    print(f"\n  Total: ₹{total:,.2f}  |  {len(expenses)} expense(s) shown")

    show_summary = _ask("\n  Show category breakdown? (Y/n)", "y")
    if show_summary.lower() != "n":
        totals = get_category_totals(start or None, end or None)
        if totals:
            print(f"\n  {'Category':<20} {'Amount':>12}")
            print(f"  {'─'*20} {'─'*12}")
            for cat, amt in totals.items():
                print(f"  {cat:<20} ₹{amt:>11,.2f}")


def menu_get_advice() -> None:
    from backend.database import get_expenses, get_category_totals
    from backend.config import get_llm, LLM_PROVIDER, GOOGLE_MODEL, OPENAI_MODEL

    _header("Financial Advice")

    try:
        llm = get_llm()
    except EnvironmentError as e:
        print(f"  ✗ {e}")
        return

    income = _ask_float("Your monthly income (₹)")

    # Collect recent expenses
    this_month = date.today().strftime("%Y-%m")
    start = f"{this_month}-01"
    expenses = get_expenses(start_date=start, limit=200)
    category_totals = get_category_totals(start_date=start)

    philosophies = ["general", "warren_buffett", "robert_kiyosaki", "ramit_sethi"]
    philosophy = _pick("Choose an advisory philosophy", philosophies)

    question = _ask("Any specific question? (leave blank for general advice)", "")

    total_spent = sum(category_totals.values())
    savings = income - total_spent

    # Build prompt
    cat_lines = "\n".join(
        f"  - {cat}: ₹{amt:,.2f}" for cat, amt in category_totals.items()
    ) or "  No expenses recorded this month."

    philosophy_context = {
        "warren_buffett": "Apply Warren Buffett's value investing principles: live below your means, avoid debt, invest in quality assets long-term.",
        "robert_kiyosaki": "Apply Robert Kiyosaki's Rich Dad philosophy: focus on assets vs liabilities, passive income, and financial education.",
        "ramit_sethi": "Apply Ramit Sethi's approach: automate savings, spend guilt-free on what you love, cut ruthlessly on what you don't.",
        "general": "Provide balanced, practical personal finance advice suitable for an Indian household.",
    }

    prompt = f"""You are a personal finance advisor. {philosophy_context[philosophy]}

User's financial snapshot for {this_month}:
- Monthly income: ₹{income:,.2f}
- Total spent: ₹{total_spent:,.2f}
- Estimated savings: ₹{savings:,.2f} ({(savings/income*100):.1f}% of income)

Spending by category:
{cat_lines}

{f"User's question: {question}" if question else "Provide a concise analysis and 3 actionable recommendations."}

Keep your response concise (under 300 words). Use ₹ for currency. Be specific to their numbers.
Add a one-line disclaimer at the end."""

    print("\n  Generating advice…")
    try:
        response = llm.invoke(prompt)
        from backend.config import extract_llm_text
        advice = extract_llm_text(response)
        print(f"\n{'─'*50}")
        print(advice)
        print(f"{'─'*50}")
    except Exception as e:
        print(f"  ✗ LLM error: {e}")


def menu_set_budget() -> None:
    from backend.database import save_budget, get_budget
    from backend.config import EXPENSE_CATEGORIES

    _header("Set Monthly Budget")

    this_month = date.today().strftime("%Y-%m")
    month = _ask("Month (YYYY-MM)", this_month)

    existing = get_budget(month)
    if existing:
        print(f"  Existing budget found for {month} (income: ₹{existing['income']:,.2f})")

    income = _ask_float("Monthly income (₹)")

    print("\n  Enter budget for each category (0 to skip):\n")
    budgets: dict[str, float] = {}
    for cat in EXPENSE_CATEGORIES:
        existing_amt = existing.get("categories", {}).get(cat, 0)
        raw = _ask(f"  {cat}", str(existing_amt) if existing_amt else "0")
        try:
            amt = float(raw.replace(",", ""))
            if amt > 0:
                budgets[cat] = amt
        except ValueError:
            pass

    save_budget(month, income, budgets)
    total = sum(budgets.values())
    print(f"\n  ✓ Budget saved for {month}")
    print(f"  Total budgeted: ₹{total:,.2f} / ₹{income:,.2f} income")
    if total > income:
        print(f"  ⚠  Budget exceeds income by ₹{total - income:,.2f}")


def menu_delete_expense() -> None:
    from backend.database import get_expense_by_id, delete_expense

    _header("Delete Expense")

    raw = _ask("Expense ID to delete")
    if not raw.isdigit():
        print("  Invalid ID.")
        return

    expense_id = int(raw)
    expense = get_expense_by_id(expense_id)
    if not expense:
        print(f"  No expense found with id={expense_id}")
        return

    print(f"\n  {expense['date']}  {expense['merchant']}  ₹{expense['amount']:,.2f}  ({expense['category']})")
    confirm = _ask("  Delete this expense? (y/N)", "n")
    if confirm.lower() == "y":
        delete_expense(expense_id)
        print("  ✓ Deleted.")
    else:
        print("  Cancelled.")


# ── Main loop ─────────────────────────────────────────────────────────────────

MENU_OPTIONS = [
    ("Add expense manually",        menu_add_expense),
    ("Scan receipt / screenshot",   menu_scan_receipt),
    ("View expenses",               menu_view_expenses),
    ("Get AI financial advice",     menu_get_advice),
    ("Set monthly budget",          menu_set_budget),
    ("Delete an expense",           menu_delete_expense),
    ("Exit",                        None),
]


def main() -> None:
    print("\n╔══════════════════════════════════════╗")
    print("║   Financial Research Advisor  v1.0   ║")
    print("╚══════════════════════════════════════╝")

    while True:
        _header("Main Menu")
        for i, (label, _) in enumerate(MENU_OPTIONS, 1):
            print(f"  {i}. {label}")

        choice = input(f"\nChoose an option [1-{len(MENU_OPTIONS)}]: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU_OPTIONS)):
            print("  Invalid option.")
            continue

        label, handler = MENU_OPTIONS[int(choice) - 1]
        if handler is None:
            print("\n  Goodbye!\n")
            sys.exit(0)

        try:
            handler()
        except KeyboardInterrupt:
            print("\n  (interrupted)")
        except Exception as e:
            print(f"\n  ✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
