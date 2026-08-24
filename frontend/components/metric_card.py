"""
FinMate AI - Metric Card Component
====================================
Renders styled KPI tiles used on the Dashboard and Budget pages.
"""

import streamlit as st
from frontend.styles import COLORS


def metric_card(
    label: str,
    value: str,
    delta: str = "",
    icon: str = "",
    accent_color: str | None = None,
    col=None,
    small_text: bool = False,
) -> None:
    """
    Render a single metric card.

    Args:
        label:       Short uppercase label, e.g. "TOTAL SPENDING"
        value:       Main display value, e.g. "₹24,500"
        delta:       Optional sub-text
        icon:        Optional emoji icon
        accent_color: Override the teal accent for the value text
        col:         If provided, render inside this st.column context
        small_text:  Use smaller, auto-fitting font (for long category names)
    """
    color = accent_color or COLORS["accent_teal"]

    # Auto-detect if the value is long text (not a currency / short number)
    # and scale the font size down accordingly
    char_count = len(value)
    if small_text or char_count > 10:
        font_size = "1.05rem"
        white_space = "normal"
        word_break = "break-word"
        line_height = "1.25"
    elif char_count > 7:
        font_size = "1.35rem"
        white_space = "nowrap"
        word_break = "normal"
        line_height = "1.2"
    else:
        font_size = "1.7rem"
        white_space = "nowrap"
        word_break = "normal"
        line_height = "1.2"

    html = f"""
    <div class="fm-metric-card">
        {'<div class="fm-metric-icon">' + icon + '</div>' if icon else ''}
        <div class="fm-metric-label">{label}</div>
        <div class="fm-metric-value" style="
            color:{color};
            font-size:{font_size};
            white-space:{white_space};
            word-break:{word_break};
            line-height:{line_height};
            overflow-wrap:break-word;
        ">{value}</div>
        {'<div class="fm-metric-delta">' + delta + '</div>' if delta else ''}
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def render_kpi_row(metrics: list[dict]) -> None:
    """
    Render a horizontal row of metric cards.

    Each dict in `metrics` can contain:
        label, value, delta (opt), icon (opt), accent_color (opt), small_text (opt)
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            metric_card(
                label=m.get("label", ""),
                value=m.get("value", "—"),
                delta=m.get("delta", ""),
                icon=m.get("icon", ""),
                accent_color=m.get("accent_color"),
                small_text=m.get("small_text", False),
            )
