"""
FinMate AI - Global Styles
===========================
Injects custom CSS to make the app look like a professional fintech dashboard.
Call apply_styles() once at the top of app.py.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Colour palette (dark navy + accent teal/green)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_primary":    "#0F1923",   # main background
    "bg_card":       "#1A2634",   # card / sidebar
    "bg_card_hover": "#1F2E3E",
    "accent_teal":   "#00D4AA",   # primary accent
    "accent_blue":   "#3B82F6",   # secondary accent
    "accent_orange": "#F59E0B",   # warning / budget
    "accent_red":    "#EF4444",   # danger / over-budget
    "accent_green":  "#10B981",   # success / savings
    "text_primary":  "#F1F5F9",
    "text_muted":    "#94A3B8",
    "border":        "#2D3F55",
}

# Plotly / chart colours — consistent across all charts
CHART_PALETTE = [
    "#00D4AA", "#3B82F6", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#10B981", "#F97316",
    "#06B6D4", "#84CC16",
]


def apply_styles() -> None:
    """Inject all custom CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# The full CSS block
# ---------------------------------------------------------------------------
_CSS = f"""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root / Base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

/* ── Hide default Streamlit decoration ── */
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
header    {{ visibility: hidden; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {COLORS['bg_card']};
    border-right: 1px solid {COLORS['border']};
}}
[data-testid="stSidebar"] .stRadio label {{
    font-size: 0.95rem;
    padding: 6px 4px;
    color: {COLORS['text_primary']};
}}

/* ── Main content padding ── */
.block-container {{
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1200px;
}}

/* ── Page title ── */
h1 {{ color: {COLORS['text_primary']}; font-weight: 700; font-size: 1.75rem; }}
h2 {{ color: {COLORS['text_primary']}; font-weight: 600; font-size: 1.35rem; }}
h3 {{ color: {COLORS['text_muted']};   font-weight: 500; font-size: 1.1rem;  }}

/* ── Metric cards ── */
.fm-metric-card {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.fm-metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,212,170,0.12);
}}
.fm-metric-label {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {COLORS['text_muted']};
    margin-bottom: 6px;
}}
.fm-metric-value {{
    font-size: 1.7rem;
    font-weight: 700;
    color: {COLORS['accent_teal']};
    line-height: 1.2;
}}
.fm-metric-delta {{
    font-size: 0.78rem;
    color: {COLORS['text_muted']};
    margin-top: 4px;
}}
.fm-metric-icon {{
    font-size: 1.5rem;
    margin-bottom: 6px;
}}

/* ── Section cards ── */
.fm-card {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}}

/* ── Expense row ── */
.fm-expense-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 0.8rem;
    border-radius: 8px;
    border: 1px solid {COLORS['border']};
    margin-bottom: 0.5rem;
    background: {COLORS['bg_card']};
    transition: background 0.15s;
}}
.fm-expense-row:hover {{ background: {COLORS['bg_card_hover']}; }}
.fm-expense-merchant {{ font-weight: 600; font-size: 0.95rem; }}
.fm-expense-meta     {{ font-size: 0.78rem; color: {COLORS['text_muted']}; }}
.fm-expense-amount   {{ font-weight: 700; font-size: 1.05rem; color: {COLORS['accent_teal']}; }}

/* ── Category badges ── */
.fm-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}}
.badge-food          {{ background: rgba(16,185,129,0.18); color: #10B981; }}
.badge-transport     {{ background: rgba(59,130,246,0.18); color: #3B82F6; }}
.badge-shopping      {{ background: rgba(245,158,11,0.18); color: #F59E0B; }}
.badge-entertainment {{ background: rgba(139,92,246,0.18); color: #8B5CF6; }}
.badge-utilities     {{ background: rgba(6,182,212,0.18);  color: #06B6D4; }}
.badge-healthcare    {{ background: rgba(239,68,68,0.18);  color: #EF4444; }}
.badge-education     {{ background: rgba(132,204,22,0.18); color: #84CC16; }}
.badge-rent          {{ background: rgba(249,115,22,0.18); color: #F97316; }}
.badge-others        {{ background: rgba(148,163,184,0.18);color: #94A3B8; }}

/* ── Progress bars ── */
.fm-progress-wrap {{
    background: {COLORS['border']};
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin: 4px 0 2px 0;
}}
.fm-progress-bar {{
    height: 10px;
    border-radius: 6px;
    transition: width 0.4s ease;
}}

/* ── Goal card ── */
.fm-goal-card {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}}
.fm-goal-title  {{ font-weight: 700; font-size: 1rem; margin-bottom: 4px; }}
.fm-goal-amount {{ font-size: 0.85rem; color: {COLORS['text_muted']}; }}
.fm-goal-pct    {{ font-weight: 700; color: {COLORS['accent_teal']}; }}

/* ── Advice card ── */
.fm-advice-card {{
    background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #1a2f3f 100%);
    border: 1px solid {COLORS['accent_teal']}44;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}}
.fm-advice-section-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {COLORS['accent_teal']};
    margin-bottom: 4px;
}}
.fm-advice-text {{
    font-size: 0.95rem;
    line-height: 1.65;
    color: {COLORS['text_primary']};
}}

/* ── Mock/demo banner ── */
.fm-mock-banner {{
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: {COLORS['accent_orange']};
    margin-bottom: 1rem;
}}

/* ── Divider ── */
.fm-divider {{
    border: none;
    border-top: 1px solid {COLORS['border']};
    margin: 1rem 0;
}}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > textarea {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_primary']};
    border-radius: 8px;
}}
.stSelectbox > div > div {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_primary']};
    border-radius: 8px;
}}
.stDateInput > div > div > input {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_primary']};
}}
.stButton > button {{
    background: linear-gradient(135deg, {COLORS['accent_teal']}, #00b894);
    color: #0F1923;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    transition: opacity 0.2s;
}}
.stButton > button:hover {{ opacity: 0.88; }}

/* ── DataFrame / table ── */
.dataframe {{
    background: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    font-size: 0.88rem;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid {COLORS['border']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {COLORS['text_muted']};
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1.1rem;
    font-size: 0.9rem;
    font-weight: 500;
}}
.stTabs [aria-selected="true"] {{
    background: {COLORS['bg_card']};
    color: {COLORS['accent_teal']};
    font-weight: 700;
}}

/* ── Upload area ── */
[data-testid="stFileUploader"] {{
    background: {COLORS['bg_card']};
    border: 2px dashed {COLORS['border']};
    border-radius: 12px;
    padding: 1rem;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar       {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {COLORS['bg_primary']}; }}
::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 3px; }}

/* ── Top navbar ── */
.fm-topnav {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 0.5rem 0.75rem;
    margin-bottom: 1.2rem;
}}
.fm-topnav a {{
    text-decoration: none;
    font-size: 0.82rem;
    font-weight: 600;
    color: {COLORS['text_muted']};
    padding: 4px 10px;
    border-radius: 6px;
    transition: background 0.15s, color 0.15s;
    white-space: nowrap;
}}
.fm-topnav a:hover {{
    background: {COLORS['bg_card_hover']};
    color: {COLORS['text_primary']};
}}
.fm-topnav a.active {{
    background: {COLORS['accent_teal']}22;
    color: {COLORS['accent_teal']};
    border: 1px solid {COLORS['accent_teal']}44;
}}
.fm-topnav-sep {{
    color: {COLORS['border']};
    font-size: 0.9rem;
    user-select: none;
}}
</style>
"""
