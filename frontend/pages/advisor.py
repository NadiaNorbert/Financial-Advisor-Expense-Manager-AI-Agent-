"""
FinMate AI - AI Financial Advisor Page
=========================================
Spending summary + guru selector + AI advice display.
"""

from __future__ import annotations

import streamlit as st

from frontend.styles import COLORS
from backend.adapter import (
    get_spending_summary,
    get_budget_settings,
    generate_financial_advice,
    GURU_PROMPTS,
)


# Guru metadata for display cards
_GURU_META = {
    "General Financial Principles": {
        "emoji": "📚",
        "tagline": "Universal money rules — save, budget, invest.",
        "color": COLORS["accent_teal"],
    },
    "Warren Buffett": {
        "emoji": "💼",
        "tagline": "Value investing & long-term compounding.",
        "color": "#F59E0B",
    },
    "Robert Kiyosaki": {
        "emoji": "🏠",
        "tagline": "Assets vs liabilities & passive income.",
        "color": "#8B5CF6",
    },
    "Ramit Sethi": {
        "emoji": "🚀",
        "tagline": "Automation, guilt-free spending & big wins.",
        "color": "#3B82F6",
    },
}


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>💡 AI Financial Advisor</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Get personalised financial insights based on your spending patterns.</p>",
        unsafe_allow_html=True,
    )

    # ── Disclaimer ────────────────────────────────────────────────
    st.info(
        "📌 **Disclaimer:** This feature provides educational financial information "
        "for learning purposes only. It is not a substitute for advice from a qualified "
        "financial professional. Past spending patterns do not guarantee future outcomes.",
        icon="ℹ️",
    )

    summary  = get_spending_summary()
    settings = get_budget_settings()

    # ── Spending Snapshot ─────────────────────────────────────────
    st.markdown("### Your Spending Snapshot")
    _spending_snapshot(summary, settings)

    # ── Guru selection ────────────────────────────────────────────
    st.markdown("### Choose Your Financial Philosophy")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Select a financial guru whose philosophy resonates with you. "
        "The AI advisor will frame its analysis through their lens.</p>",
        unsafe_allow_html=True,
    )

    gurus = list(GURU_PROMPTS.keys())
    guru_cols = st.columns(len(gurus))
    for col, guru in zip(guru_cols, gurus):
        meta = _GURU_META.get(guru, {"emoji": "💡", "tagline": "", "color": COLORS["accent_teal"]})
        is_selected = st.session_state.get("selected_guru") == guru
        border = f"2px solid {meta['color']}" if is_selected else f"1px solid {COLORS['border']}"
        with col:
            st.markdown(
                f"""
                <div style="
                    background:{COLORS['bg_card']};
                    border:{border};
                    border-radius:12px;
                    padding:1rem;
                    text-align:center;
                    cursor:pointer;
                    min-height:110px;
                ">
                    <div style="font-size:2rem;">{meta['emoji']}</div>
                    <div style="font-weight:700; font-size:0.88rem;
                                color:{meta['color']}; margin:4px 0 2px 0;">
                        {guru}
                    </div>
                    <div style="font-size:0.72rem; color:{COLORS['text_muted']};">
                        {meta['tagline']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if col.button(
                "Select" if not is_selected else "✓ Selected",
                key=f"guru_{guru}",
                use_container_width=True,
            ):
                st.session_state.selected_guru = guru
                st.session_state.advice_result = None  # clear old advice
                st.rerun()

    selected_guru = st.session_state.get("selected_guru", gurus[0])
    st.markdown(
        f"<p style='margin-top:0.5rem; font-size:0.85rem; color:{COLORS['text_muted']};'>"
        f"Selected: <strong style='color:{COLORS['accent_teal']};'>{selected_guru}</strong></p>",
        unsafe_allow_html=True,
    )

    # ── Analyse button ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    analyse_clicked = st.button(
        "🔍  Analyse My Finances",
        use_container_width=True,
        type="primary",
    )

    if analyse_clicked:
        if summary.get("transaction_count", 0) == 0:
            st.warning("No expense data found. Add some expenses first.")
        else:
            with st.spinner("Analysing your finances… this may take up to 15 seconds ⏳"):
                try:
                    advice = generate_financial_advice(summary, selected_guru)
                    st.session_state.advice_result = advice
                    st.session_state.advice_guru   = selected_guru
                except Exception as e:
                    st.error(f"Could not generate advice: {e}")
                    return

    # ── Display advice ────────────────────────────────────────────
    advice = st.session_state.get("advice_result")
    if advice:
        _render_advice(advice)


# ---------------------------------------------------------------------------
# Spending Snapshot
# ---------------------------------------------------------------------------

def _spending_snapshot(summary: dict, settings: dict) -> None:
    total_spent   = summary.get("total_spending", 0)
    monthly_spent = summary.get("monthly_spending", 0)
    top_cat       = summary.get("top_category", "N/A")
    tx_count      = summary.get("transaction_count", 0)
    income        = settings.get("income", 0)
    savings_est   = income - monthly_spent if income > 0 else None
    by_cat        = summary.get("by_category", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-label">Total Spending</div>'
            f'<div class="fm-metric-value">₹{total_spent:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-label">This Month</div>'
            f'<div class="fm-metric-value">₹{monthly_spent:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-label">Top Category</div>'
            f'<div class="fm-metric-value" style="font-size:1.1rem;">{top_cat}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        savings_str = f"₹{savings_est:,.0f}" if savings_est is not None else "N/A"
        savings_color = (
            COLORS["accent_green"] if savings_est and savings_est > 0 else
            COLORS["accent_red"]
        )
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-label">Est. Monthly Savings</div>'
            f'<div class="fm-metric-value" style="color:{savings_color};">{savings_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Top categories mini table
    if by_cat:
        st.markdown("<br>", unsafe_allow_html=True)
        top5 = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:5]
        cols = st.columns(len(top5))
        for col, (cat, amt) in zip(cols, top5):
            pct = amt / total_spent * 100 if total_spent else 0
            with col:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding:0.5rem;
                                background:{COLORS['bg_card']};
                                border:1px solid {COLORS['border']};
                                border-radius:8px;">
                        <div style="font-size:0.72rem; color:{COLORS['text_muted']};
                                    text-transform:uppercase; margin-bottom:2px;">{cat}</div>
                        <div style="font-weight:700; font-size:1rem;
                                    color:{COLORS['accent_teal']};">₹{amt:,.0f}</div>
                        <div style="font-size:0.7rem; color:{COLORS['text_muted']};">
                            {pct:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Advice Display
# ---------------------------------------------------------------------------

def _render_advice(advice: dict) -> None:
    guru = advice.get("guru", "General Financial Principles")
    is_mock = advice.get("_mock", False)
    reason  = advice.get("_reason", "")
    meta = _GURU_META.get(guru, {"emoji": "💡", "color": COLORS["accent_teal"]})

    if is_mock:
        # Determine the right message based on why fallback was used
        if "No API key" in reason or "api_key" in reason.lower():
            banner_text = (
                "🔑 <strong>No API key found.</strong> "
                "Add <code>GOOGLE_API_KEY</code> to your <code>.env</code> file to enable live AI advice. "
                "Showing pre-written template advice for now."
            )
        elif reason:
            # LLM was called but failed (wrong model, network, quota, etc.)
            short_reason = reason[:120] + "…" if len(reason) > 120 else reason
            banner_text = (
                f"⚡ <strong>AI call failed:</strong> {short_reason} "
                "— showing template advice."
            )
        else:
            banner_text = (
                "⚡ <strong>Template advice</strong> — AI advisor is using offline responses."
            )

        st.markdown(
            f'<div class="fm-mock-banner">{banner_text}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="
            display:flex; align-items:center; gap:10px;
            margin:1.5rem 0 0.75rem 0;
        ">
            <div style="font-size:2rem;">{meta['emoji']}</div>
            <div>
                <div style="font-weight:700; font-size:1.1rem; color:{meta['color']};">
                    {guru}
                </div>
                <div style="font-size:0.8rem; color:{COLORS['text_muted']};">
                    AI-generated financial analysis
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sections = [
        ("📊 Spending Observation",  advice.get("observation",    "")),
        ("💡 Recommendation",        advice.get("recommendation", "")),
        ("❓ Why?",                   advice.get("why",            "")),
        ("✅ Suggested Action",       advice.get("action",         "")),
    ]

    for title, content in sections:
        if content:
            st.markdown(
                f"""
                <div class="fm-advice-card">
                    <div class="fm-advice-section-title">{title}</div>
                    <div class="fm-advice-text">{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Save advice to session for reports
    st.session_state["last_advice"] = advice

    # Disclaimer
    st.markdown(
        f"""
        <div style="
            margin-top:1rem;
            padding:0.8rem 1rem;
            background:rgba(59,130,246,0.08);
            border:1px solid rgba(59,130,246,0.25);
            border-radius:8px;
            font-size:0.78rem;
            color:{COLORS['text_muted']};
        ">
            ⚖️ <strong>Disclaimer:</strong> This application provides educational financial
            information and is not a substitute for advice from a qualified financial professional.
            Always consult a certified financial planner before making significant financial decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )
