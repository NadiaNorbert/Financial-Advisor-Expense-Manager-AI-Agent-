"""
FinMate AI - Goals Page
=========================
Savings goal tracker with add / edit / delete and progress gauges.
"""

from __future__ import annotations

import datetime
import streamlit as st

from frontend.styles import COLORS
from frontend.components.charts import goal_gauge
from backend.adapter import get_goals, save_goal, update_goal, delete_goal


def render() -> None:
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>🎯 Savings Goals</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Define financial goals, track your progress, and stay motivated.</p>",
        unsafe_allow_html=True,
    )

    tab_list, tab_add = st.tabs(["📋  My Goals", "➕  Add Goal"])

    with tab_list:
        _goals_list()

    with tab_add:
        _add_goal_form()


# ---------------------------------------------------------------------------
# Goals List
# ---------------------------------------------------------------------------

def _goals_list() -> None:
    goals = get_goals()

    if not goals:
        st.info("No goals yet. Use the **Add Goal** tab to create your first savings goal.")
        return

    # Summary row
    total_target  = sum(g.get("target", 0) for g in goals)
    total_current = sum(g.get("current", 0) for g in goals)
    overall_pct   = total_current / total_target * 100 if total_target else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">🎯</div>'
            f'<div class="fm-metric-label">Active Goals</div>'
            f'<div class="fm-metric-value">{len(goals)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">💰</div>'
            f'<div class="fm-metric-label">Total Target</div>'
            f'<div class="fm-metric-value">₹{total_target:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="fm-metric-card">'
            f'<div class="fm-metric-icon">✅</div>'
            f'<div class="fm-metric-label">Overall Progress</div>'
            f'<div class="fm-metric-value" style="color:{COLORS["accent_green"]};">'
            f'{overall_pct:.1f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Individual goal cards
    for goal in goals:
        _goal_card(goal)


def _goal_card(goal: dict) -> None:
    gid     = goal["id"]
    name    = goal.get("name", "Goal")
    target  = goal.get("target", 0)
    current = goal.get("current", 0)
    deadline = goal.get("deadline", "")
    notes   = goal.get("notes", "")
    pct     = min(current / target * 100, 100) if target > 0 else 0
    bar_color = (
        COLORS["accent_red"]    if pct < 25 else
        COLORS["accent_orange"] if pct < 60 else
        COLORS["accent_green"]
    )

    # Days remaining
    days_left_str = ""
    if deadline:
        try:
            dl   = datetime.date.fromisoformat(str(deadline))
            diff = (dl - datetime.date.today()).days
            days_left_str = (
                f"🕐 {diff} days left" if diff > 0 else
                "🏁 Deadline passed" if diff < 0 else
                "📅 Due today!"
            )
        except ValueError:
            pass

    with st.container():
        col_info, col_gauge, col_actions = st.columns([3, 2, 1])

        with col_info:
            st.markdown(
                f"""
                <div class="fm-goal-card">
                    <div class="fm-goal-title">{name}</div>
                    <div class="fm-goal-amount">
                        <span class="fm-goal-pct">₹{current:,.0f}</span>
                        &nbsp;of&nbsp; ₹{target:,.0f}
                    </div>
                    <div style="margin-top:6px;">
                        <div class="fm-progress-wrap">
                            <div class="fm-progress-bar"
                                 style="width:{pct:.1f}%; background:{bar_color};"></div>
                        </div>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                margin-top:4px; font-size:0.75rem;
                                color:{COLORS['text_muted']};">
                        <span>{pct:.1f}% complete</span>
                        <span>{days_left_str}</span>
                    </div>
                    {'<div style="font-size:0.75rem; color:' + COLORS["text_muted"] + '; margin-top:4px;">📝 ' + notes + '</div>' if notes else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_gauge:
            st.plotly_chart(
                goal_gauge(name, current, target),
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"gauge_{gid}",
            )

        with col_actions:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✏️ Edit", key=f"edit_goal_{gid}", use_container_width=True):
                st.session_state[f"editing_goal_{gid}"] = True
            if st.button("🗑️ Delete", key=f"del_goal_{gid}", use_container_width=True):
                result = delete_goal(gid)
                if result["success"]:
                    st.success(f"Deleted: {name}")
                    st.rerun()
                else:
                    st.error(result["message"])

        # Inline edit form
        if st.session_state.get(f"editing_goal_{gid}", False):
            _goal_edit_form(goal)


def _goal_edit_form(goal: dict) -> None:
    gid = goal["id"]
    with st.form(f"edit_goal_{gid}"):
        st.markdown(f"**Edit: {goal.get('name', 'Goal')}**")
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Goal Name", value=goal.get("name", ""))
        with c2:
            new_target = st.number_input(
                "Target Amount (₹)", min_value=1.0,
                value=float(goal.get("target", 1000)), format="%.0f"
            )
        c3, c4 = st.columns(2)
        with c3:
            new_current = st.number_input(
                "Current Savings (₹)", min_value=0.0,
                value=float(goal.get("current", 0)), format="%.0f"
            )
        with c4:
            dl = goal.get("deadline", str(datetime.date.today()))
            try:
                dl_date = datetime.date.fromisoformat(str(dl)[:10])
            except ValueError:
                dl_date = datetime.date.today()
            new_deadline = st.date_input("Target Deadline", value=dl_date)

        new_notes = st.text_input("Notes", value=goal.get("notes", ""))

        c_save, c_cancel = st.columns(2)
        with c_save:
            save = st.form_submit_button("💾 Save", use_container_width=True)
        with c_cancel:
            cancel = st.form_submit_button("✕ Cancel", use_container_width=True)

    if save:
        result = update_goal(gid, {
            "name":     new_name,
            "target":   new_target,
            "current":  new_current,
            "deadline": str(new_deadline),
            "notes":    new_notes,
        })
        if result["success"]:
            st.success("Goal updated!")
            st.session_state[f"editing_goal_{gid}"] = False
            st.rerun()
        else:
            st.error(result["message"])

    if cancel:
        st.session_state[f"editing_goal_{gid}"] = False
        st.rerun()


# ---------------------------------------------------------------------------
# Add Goal Form
# ---------------------------------------------------------------------------

def _add_goal_form() -> None:
    st.markdown("#### Add a New Savings Goal")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Set a clear target and track your savings progress over time.</p>",
        unsafe_allow_html=True,
    )

    with st.form("add_goal_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Goal Name *", placeholder="e.g. Emergency Fund")
        with c2:
            target = st.number_input("Target Amount (₹) *", min_value=1.0, step=500.0, format="%.0f")

        c3, c4 = st.columns(2)
        with c3:
            current = st.number_input("Current Savings (₹)", min_value=0.0, step=100.0, format="%.0f")
        with c4:
            deadline = st.date_input(
                "Target Deadline *",
                value=datetime.date.today() + datetime.timedelta(days=180),
            )

        notes = st.text_input("Notes (optional)", placeholder="Describe your goal…")
        submitted = st.form_submit_button("🎯  Add Goal", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Goal name is required.")
            return
        if target <= 0:
            st.error("Target amount must be greater than zero.")
            return
        if current > target:
            st.warning("Current savings is greater than the target — goal is already achieved!")

        result = save_goal({
            "name":     name.strip(),
            "target":   target,
            "current":  current,
            "deadline": str(deadline),
            "notes":    notes.strip(),
        })
        if result.get("success"):
            st.success(f"✅ Goal '{name}' created! (ID #{result.get('id', '?')})")
            st.balloons()
        else:
            st.error(f"Error: {result.get('message')}")
