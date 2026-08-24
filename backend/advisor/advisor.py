"""
advisor.py – AI Financial Advisor
===================================
Generates personalised financial advice using LangChain + the configured LLM
(OpenAI gpt-4o-mini by default, or Google Gemini via LLM_PROVIDER=google).

Public API
----------
    generate_financial_advice(summary: dict, guru: str = "General Financial Principles") -> dict
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Philosophy prompts ────────────────────────────────────────────────────────

_PHILOSOPHY_MAP: dict[str, str] = {
    "General Financial Principles": (
        "Provide balanced, practical personal finance advice grounded in universal "
        "principles: emergency fund first, avoid high-interest debt, invest early, "
        "and live within your means. Tailor advice to an Indian household context."
    ),
    "Warren Buffett": (
        "Apply Warren Buffett's philosophy: live well below your means, avoid "
        "unnecessary debt, invest only in what you understand, and think long-term. "
        "Focus on value, not speculation. Every rupee saved is a future compounding engine."
    ),
    "Robert Kiyosaki": (
        "Apply Robert Kiyosaki's Rich Dad Poor Dad philosophy: distinguish between "
        "assets (things that put money in your pocket) and liabilities (things that "
        "take money out). Encourage building passive income streams and financial education."
    ),
    "Ramit Sethi": (
        "Apply Ramit Sethi's I Will Teach You To Be Rich philosophy: automate savings "
        "and investments on payday before spending, spend guilt-free on things you love, "
        "cut mercilessly on things you don't. Fix big structural levers — not small habits."
    ),
}

# Fallback offline advice templates when LLM is unavailable
_FALLBACK_ADVICE: dict[str, dict] = {
    "General Financial Principles": {
        "observation": "Your discretionary spending (Food, Shopping, Entertainment) forms a significant portion of your monthly expenses.",
        "recommendation": "Follow the 50/30/20 rule — 50% on needs, 30% on wants, 20% on savings and investments.",
        "why": "A structured budget prevents lifestyle inflation and ensures you save consistently regardless of income level.",
        "action": "Set up an automatic transfer of at least 20% of your income to savings on the day your salary arrives.",
    },
    "Warren Buffett": {
        "observation": "Several recurring discretionary expenses are consuming capital that could be compounding in your favour.",
        "recommendation": "Ruthlessly cut recurring expenses that don't appreciate. Redirect that capital to a diversified index fund.",
        "why": "Buffett's first rule: never lose money. Every rupee wasted on lifestyle inflation is a rupee lost from your compounding engine.",
        "action": "Review all subscriptions. Cancel at least one. Open a SIP in a Nifty 50 index fund with the savings.",
    },
    "Robert Kiyosaki": {
        "observation": "The majority of your spending is on liabilities — expenses that drain your pocket without building wealth.",
        "recommendation": "Before every purchase, ask: is this an asset or a liability? Prioritise acquiring income-generating assets.",
        "why": "Financial freedom comes from your assets generating more income than your expenses, not from a salary.",
        "action": "Allocate even ₹500/month toward a skill, side project, or investment that can generate future passive income.",
    },
    "Ramit Sethi": {
        "observation": "You may be stressed about small daily expenses while ignoring the bigger structural financial wins available to you.",
        "recommendation": "Automate your savings and a small SIP investment first. Then spend guilt-free on the things you actually love.",
        "why": "Small daily costs are not your problem. Investing early and consistently creates wealth. Start now, not later.",
        "action": "Set up an automatic SIP of ₹2,000/month today. Automate it so it happens before you see the money.",
    },
}


def generate_financial_advice(
    summary: dict,
    guru: str = "General Financial Principles",
) -> dict:
    """Generate AI-powered financial advice using the user's spending summary.

    Parameters
    ----------
    summary:
        Output of ``backend.expenses.analyzer.get_spending_summary()`` —
        must contain at least ``total_spending``, ``monthly_spending``,
        ``by_category``, and ``transaction_count``.
        Also accepts ``income`` if available.
    guru:
        One of the supported philosophy keys.

    Returns
    -------
    dict
        Keys: ``observation``, ``recommendation``, ``why``, ``action``,
        ``guru``, ``disclaimer``, ``_mock`` (True only when LLM is unavailable).
    """
    # Normalise guru name to closest match
    philosophy_key = _closest_guru(guru)

    try:
        return _generate_llm_advice(summary, philosophy_key)
    except EnvironmentError as e:
        logger.warning("LLM unavailable (%s) — using offline template advice.", e)
        return _fallback_advice(philosophy_key, reason=f"No API key: {e}")
    except (ConnectionResetError, ConnectionError, OSError) as e:
        logger.warning("Network error reaching LLM (%s) — using offline template advice.", e)
        return _fallback_advice(philosophy_key, reason=f"Network error: {e}")
    except Exception as e:
        logger.error("LLM call failed: %s — using offline template advice.", e)
        return _fallback_advice(philosophy_key, reason=str(e))

# ── LLM-based advice ──────────────────────────────────────────────────────────

def _generate_llm_advice(summary: dict, guru: str) -> dict:
    """Call the LLM and parse the structured response."""
    from backend.config import GOOGLE_API_KEY, GOOGLE_MODEL, LLM_PROVIDER

    # Build spending context
    total_spending   = summary.get("total_spending", summary.get("total", 0))
    monthly_spending = summary.get("monthly_spending", total_spending)
    by_category      = summary.get("by_category", {})
    tx_count         = summary.get("transaction_count", summary.get("count", 0))
    income           = summary.get("income", 0)
    top_cat          = summary.get("top_category", "")

    if by_category:
        cat_lines = "\n".join(
            f"  - {cat}: ₹{amt:,.2f}" for cat, amt in
            sorted(by_category.items(), key=lambda x: x[1], reverse=True)
        )
    else:
        cat_lines = "  No category breakdown available."

    savings_line = ""
    if income:
        savings = income - monthly_spending
        savings_pct = (savings / income * 100) if income else 0
        savings_line = f"- Estimated monthly savings: ₹{savings:,.2f} ({savings_pct:.1f}% of income)\n"

    philosophy_context = _PHILOSOPHY_MAP.get(guru, _PHILOSOPHY_MAP["General Financial Principles"])

    prompt = f"""You are a personal finance advisor for an Indian user. {philosophy_context}

User's financial snapshot:
- Total spending recorded: ₹{total_spending:,.2f}
- This month's spending: ₹{monthly_spending:,.2f}
- Transactions recorded: {tx_count}
- Highest spending category: {top_cat or "N/A"}
{savings_line}
Spending by category:
{cat_lines}

Respond ONLY in this exact format (no extra text, no markdown headers):

OBSERVATION: <one sentence about their spending pattern>
RECOMMENDATION: <one clear recommendation>
WHY: <one sentence explaining the reasoning>
ACTION: <one concrete action they can take this week>

Keep each section under 60 words. Use ₹ for currency. Be specific to their numbers."""

    # Use google-genai directly (avoids LangChain compatibility issues)
    if LLM_PROVIDER == "google" and GOOGLE_API_KEY:
        raw = _call_gemini(prompt, GOOGLE_API_KEY, GOOGLE_MODEL)
    else:
        raise EnvironmentError(
            f"LLM_PROVIDER is '{LLM_PROVIDER}' but no GOOGLE_API_KEY set."
        )

    return _parse_llm_response(raw, guru)


def _call_gemini(prompt: str, api_key: str, model: str) -> str:
    """Call Gemini directly via google-genai with a 30-second timeout and 2 retries."""
    import threading
    import time
    from google import genai

    client = genai.Client(api_key=api_key)

    last_error = None
    for attempt in range(3):
        if attempt > 0:
            time.sleep(2 * attempt)  # wait 2s, then 4s before retrying

        result_holder: list = []
        error_holder:  list = []

        def _call():
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                result_holder.append(response.text)
            except Exception as exc:
                error_holder.append(exc)

        thread = threading.Thread(target=_call, daemon=True)
        thread.start()
        thread.join(timeout=30)

        if thread.is_alive():
            raise TimeoutError("Gemini response timed out after 30 seconds.")

        if result_holder:
            return result_holder[0]

        last_error = error_holder[0] if error_holder else RuntimeError("No response")
        # Only retry on 503
        if "503" not in str(last_error):
            break

    raise last_error


def _parse_llm_response(raw: str, guru: str) -> dict:
    """Parse the structured LLM output into individual sections."""
    import re

    sections = {
        "observation":    "",
        "recommendation": "",
        "why":            "",
        "action":         "",
    }

    for key in sections:
        pattern = rf"{key.upper()}:\s*(.+?)(?=\n[A-Z]+:|$)"
        match = re.search(pattern, raw, re.IGNORECASE | re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()

    # If parsing failed completely, put the whole response in observation
    if not any(sections.values()):
        sections["observation"] = raw.strip()

    return {
        **sections,
        "guru": guru,
        "disclaimer": (
            "⚠️ This is general educational information only and does NOT constitute "
            "certified financial advice. Consult a SEBI-registered financial advisor "
            "before making any investment or financial decisions."
        ),
        "_mock": False,
    }


# ── Fallback (no API key) ─────────────────────────────────────────────────────

def _fallback_advice(guru: str, reason: str = "LLM unavailable") -> dict:
    """Return a pre-written template when the LLM is unavailable."""
    template = _FALLBACK_ADVICE.get(guru, _FALLBACK_ADVICE["General Financial Principles"])
    return {
        **template,
        "guru": guru,
        "disclaimer": (
            "⚠️ This is general educational information only and does NOT constitute "
            "certified financial advice. Consult a SEBI-registered financial advisor "
            "before making any investment or financial decisions."
        ),
        "_mock": True,
        "_reason": reason,
    }


def _closest_guru(name: str) -> str:
    """Return the closest matching guru key, case-insensitive."""
    name_lower = name.lower()
    for key in _PHILOSOPHY_MAP:
        if key.lower() == name_lower:
            return key
        # partial match e.g. "buffett" → "Warren Buffett"
        if any(part.lower() in name_lower for part in key.split()):
            return key
    return "General Financial Principles"
