"""
backend/app/api/v1/goals.py
===========================
Savings goals management endpoints: create, list, update, and delete.
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.all_schemas import (
    GoalCreate,
    GoalUpdate,
    GoalOut,
)
from backend.app.core.security import get_current_user_optional
from backend.auth import (
    get_goals as db_get_goals,
    save_goal as db_save_goal,
    update_goal as db_update_goal,
    delete_goal as db_delete_goal,
)

router = APIRouter(prefix="/goals", tags=["Goals"])

# Default user ID for unauthenticated / local single user mode
DEFAULT_USER_ID = 1


@router.get("", response_model=List[GoalOut])
def list_goals(current_user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = current_user["id"] if current_user else DEFAULT_USER_ID
    goals = db_get_goals(user_id)
    return goals


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else DEFAULT_USER_ID
    res = db_save_goal(user_id, {
        "name": data.name.strip(),
        "target": float(data.target),
        "current": float(data.current),
        "deadline": str(data.deadline) if data.deadline else None,
        "notes": data.notes.strip() if data.notes else None,
    })
    
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message", "Could not create goal"))
    
    new_id = res["id"]
    goals = db_get_goals(user_id)
    matching = next((g for g in goals if g["id"] == new_id), None)
    if matching:
        return matching
    return {
        "id": new_id,
        "user_id": user_id,
        "name": data.name,
        "target": data.target,
        "current": data.current,
        "deadline": data.deadline,
        "notes": data.notes,
    }


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    data: GoalUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else DEFAULT_USER_ID
    updates = {}
    if data.name is not None:
        updates["name"] = data.name.strip()
    if data.target is not None:
        updates["target"] = float(data.target)
    if data.current is not None:
        updates["current"] = float(data.current)
    if data.deadline is not None:
        updates["deadline"] = str(data.deadline)
    if data.notes is not None:
        updates["notes"] = data.notes.strip()
        
    res = db_update_goal(goal_id, user_id, updates)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message", "Could not update goal"))
        
    goals = db_get_goals(user_id)
    matching = next((g for g in goals if g["id"] == goal_id), None)
    if not matching:
        raise HTTPException(status_code=404, detail="Goal not found after update")
    return matching


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id = current_user["id"] if current_user else DEFAULT_USER_ID
    res = db_delete_goal(goal_id, user_id)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message", "Goal not found"))
    return {"success": True, "message": "Goal deleted successfully."}
