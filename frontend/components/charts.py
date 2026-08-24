"""
FinMate AI - Chart Components
================================
All Plotly chart builders used across the app.
Each function returns a Plotly Figure object.
Call st.plotly_chart(fig, use_container_width=True) to display.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from frontend.styles import CHART_PALETTE, COLORS


# ---------------------------------------------------------------------------
# Shared layout defaults
# ---------------------------------------------------------------------------

_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text_primary"], size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(size=11),
    ),
)


def _axis_style(**kwargs) -> dict:
    return dict(
        gridcolor=COLORS["border"],
        gridwidth=1,
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"], size=11),
        title_font=dict(color=COLORS["text_muted"], size=12),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# 1. Category Donut Chart
# ---------------------------------------------------------------------------

def category_donut_chart(by_category: dict[str, float]) -> go.Figure:
    """
    Donut chart showing spending breakdown by category.
    Args:
        by_category: {category_name: amount}
    """
    if not by_category:
        return _empty_fig("No category data yet")

    labels = list(by_category.keys())
    values = [by_category[k] for k in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=CHART_PALETTE[:len(labels)], line=dict(color=COLORS["bg_primary"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))

    total = sum(values)
    fig.add_annotation(
        text=f"₹{total:,.0f}",
        x=0.5, y=0.5,
        font=dict(size=16, color=COLORS["accent_teal"], family="Inter"),
        showarrow=False,
    )

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Spending by Category", font=dict(size=14, color=COLORS["text_primary"])),
        showlegend=True,
        height=340,
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Monthly Bar Chart
# ---------------------------------------------------------------------------

def monthly_bar_chart(monthly_trend: list[dict]) -> go.Figure:
    """
    Bar chart of monthly spending.
    Args:
        monthly_trend: [{"month": "2026-07", "amount": 18000}, ...]
    """
    if not monthly_trend:
        return _empty_fig("No monthly data yet")

    df = pd.DataFrame(monthly_trend)
    df["month_label"] = pd.to_datetime(df["month"]).dt.strftime("%b %Y")

    fig = go.Figure(go.Bar(
        x=df["month_label"],
        y=df["amount"],
        marker=dict(
            color=df["amount"],
            colorscale=[[0, COLORS["accent_blue"]], [1, COLORS["accent_teal"]]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        text=[f"₹{v:,.0f}" for v in df["amount"]],
        textposition="outside",
        textfont=dict(size=10, color=COLORS["text_muted"]),
    ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Monthly Spending", font=dict(size=14, color=COLORS["text_primary"])),
        xaxis=_axis_style(title="Month"),
        yaxis=_axis_style(title="Amount (₹)", tickprefix="₹"),
        height=320,
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Spending Trend Line Chart
# ---------------------------------------------------------------------------

def spending_trend_chart(daily_spending: list[dict]) -> go.Figure:
    """
    Smooth line chart of daily cumulative / per-day spending.
    Args:
        daily_spending: [{"date": "2026-08-01", "amount": 450}, ...]
    """
    if not daily_spending:
        return _empty_fig("No daily data yet")

    df = pd.DataFrame(daily_spending)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["cumulative"] = df["amount"].cumsum()

    fig = go.Figure()

    # Cumulative area
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["cumulative"],
        name="Cumulative",
        line=dict(color=COLORS["accent_teal"], width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba(0,212,170,0.08)",
        hovertemplate="<b>%{x|%d %b}</b><br>Cumulative: ₹%{y:,.0f}<extra></extra>",
    ))

    # Daily bars (secondary)
    fig.add_trace(go.Bar(
        x=df["date"], y=df["amount"],
        name="Daily",
        marker=dict(color=COLORS["accent_blue"], opacity=0.5),
        hovertemplate="<b>%{x|%d %b}</b><br>Daily: ₹%{y:,.0f}<extra></extra>",
        yaxis="y2",
    ))

    # Build layout without 'legend' from _LAYOUT_BASE to avoid duplicate key
    _base = {k: v for k, v in _LAYOUT_BASE.items() if k != "legend"}
    fig.update_layout(
        **_base,
        title=dict(text="Spending Trend", font=dict(size=14, color=COLORS["text_primary"])),
        xaxis=_axis_style(title="Date"),
        yaxis=_axis_style(title="Cumulative (₹)", tickprefix="₹"),
        yaxis2=dict(
            **_axis_style(title="Daily (₹)"),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(**_LAYOUT_BASE["legend"], orientation="h", y=1.08, x=0),
        height=320,
        barmode="overlay",
    )
    return fig


# ---------------------------------------------------------------------------
# 4. Category Bar Chart (horizontal)
# ---------------------------------------------------------------------------

def category_bar_chart(by_category: dict[str, float]) -> go.Figure:
    """
    Horizontal bar chart comparing category spending.
    """
    if not by_category:
        return _empty_fig("No category data yet")

    sorted_cats = sorted(by_category.items(), key=lambda x: x[1])
    labels = [c[0] for c in sorted_cats]
    values = [c[1] for c in sorted_cats]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=values,
            colorscale=[[0, COLORS["accent_blue"]], [1, COLORS["accent_teal"]]],
            showscale=False,
        ),
        text=[f"₹{v:,.0f}" for v in values],
        textposition="outside",
        textfont=dict(size=10, color=COLORS["text_muted"]),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Category Breakdown", font=dict(size=14, color=COLORS["text_primary"])),
        xaxis=_axis_style(title="Amount (₹)", tickprefix="₹"),
        yaxis=_axis_style(title=""),
        height=max(280, len(labels) * 36 + 80),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Budget vs Spent Bar Chart
# ---------------------------------------------------------------------------

def budget_vs_spent_chart(budget_rows: list[dict]) -> go.Figure:
    """
    Grouped bar chart comparing budget vs actual spending per category.
    Args:
        budget_rows: list of {category, budget, spent}
    """
    active = [r for r in budget_rows if r.get("budget", 0) > 0]
    if not active:
        return _empty_fig("No budget data yet")

    categories = [r["category"] for r in active]
    budgets    = [r["budget"]   for r in active]
    spents     = [r["spent"]    for r in active]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Budget",
        x=categories,
        y=budgets,
        marker_color=COLORS["accent_blue"],
        opacity=0.7,
        hovertemplate="<b>%{x}</b><br>Budget: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Spent",
        x=categories,
        y=spents,
        marker_color=COLORS["accent_teal"],
        hovertemplate="<b>%{x}</b><br>Spent: ₹%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Budget vs Actual Spending", font=dict(size=14, color=COLORS["text_primary"])),
        barmode="group",
        xaxis=_axis_style(title="Category", tickangle=-30),
        yaxis=_axis_style(title="Amount (₹)", tickprefix="₹"),
        height=340,
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Goal Progress Gauge
# ---------------------------------------------------------------------------

def goal_gauge(name: str, current: float, target: float) -> go.Figure:
    """Gauge chart for a single savings goal."""
    pct = min((current / target * 100) if target > 0 else 0, 100)

    bar_color = (
        COLORS["accent_red"]    if pct < 25 else
        COLORS["accent_orange"] if pct < 60 else
        COLORS["accent_green"]
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current,
        delta=dict(reference=target, valueformat=",.0f", prefix="₹"),
        title=dict(text=name, font=dict(size=13, color=COLORS["text_primary"])),
        number=dict(prefix="₹", valueformat=",.0f", font=dict(color=COLORS["accent_teal"])),
        gauge=dict(
            axis=dict(range=[0, target], tickprefix="₹",
                      tickfont=dict(color=COLORS["text_muted"], size=9)),
            bar=dict(color=bar_color),
            bgcolor=COLORS["border"],
            borderwidth=0,
            steps=[dict(range=[0, target], color=COLORS["bg_card"])],
            threshold=dict(
                line=dict(color=COLORS["accent_teal"], width=2),
                thickness=0.8,
                value=target,
            ),
        ),
    ))

    fig.update_layout(
        **_LAYOUT_BASE,
        height=220,
        margin=dict(l=24, r=24, t=40, b=12),
    )
    return fig


# ---------------------------------------------------------------------------
# 7. Daily Spending Bar Chart (compact)
# ---------------------------------------------------------------------------

def daily_bar_chart(daily_spending: list[dict]) -> go.Figure:
    """Compact daily spending bar chart for the last 30 days."""
    if not daily_spending:
        return _empty_fig("No daily data yet")

    df = pd.DataFrame(daily_spending[-30:])  # last 30 days
    df["date"] = pd.to_datetime(df["date"])
    df["label"] = df["date"].dt.strftime("%d %b")

    fig = go.Figure(go.Bar(
        x=df["label"],
        y=df["amount"],
        marker=dict(color=COLORS["accent_teal"], opacity=0.8),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Daily Spending (Last 30 Days)", font=dict(size=14, color=COLORS["text_primary"])),
        xaxis=_axis_style(title=""),
        yaxis=_axis_style(title="₹", tickprefix="₹"),
        height=280,
    )
    return fig


# ---------------------------------------------------------------------------
# Helper: empty placeholder figure
# ---------------------------------------------------------------------------

def _empty_fig(message: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=14, color=COLORS["text_muted"]),
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=280,
    )
    return fig
