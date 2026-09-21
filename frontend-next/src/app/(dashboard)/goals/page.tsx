"use client";

import React, { useState, useEffect } from "react";
import {
  Target,
  Plus,
  Edit2,
  Trash2,
  Calendar,
  Clock,
  CheckCircle2,
  Trophy,
  Coins,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { GoalProgressGauge } from "@/components/charts/ExpenseCharts";
import { api } from "@/lib/api";
import { formatINR, formatDate } from "@/lib/utils";
import { Goal, GoalInput } from "@/types";

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Form State
  const [formData, setFormData] = useState<GoalInput>({
    name: "",
    target: 0,
    current: 0,
    deadline: "",
    notes: "",
  });
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => {
    loadGoals();
  }, []);

  async function loadGoals() {
    setLoading(true);
    try {
      const data = await api.getGoals();
      setGoals(data);
    } catch (err) {
      console.error("Failed to load goals", err);
    } finally {
      setLoading(false);
    }
  }

  const handleOpenAdd = () => {
    const futureDate = new Date();
    futureDate.setMonth(futureDate.getMonth() + 6);
    setFormData({
      name: "",
      target: 50000,
      current: 0,
      deadline: futureDate.toISOString().split("T")[0],
      notes: "",
    });
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (goal: Goal) => {
    setEditingGoal(goal);
    setFormData({
      name: goal.name,
      target: goal.target,
      current: goal.current,
      deadline: goal.deadline || "",
      notes: goal.notes || "",
    });
  };

  const handleSaveGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || formData.target <= 0) return;

    setFormLoading(true);
    try {
      if (editingGoal) {
        const updated = await api.updateGoal(editingGoal.id, formData);
        setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
        setEditingGoal(null);
      } else {
        const created = await api.createGoal(formData);
        setGoals((prev) => [created, ...prev]);
        setIsAddModalOpen(false);
      }
    } catch (err) {
      console.error("Failed to save goal", err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteGoal = async (id: number) => {
    try {
      await api.deleteGoal(id);
      setGoals((prev) => prev.filter((g) => g.id !== id));
      setDeletingId(null);
    } catch (err) {
      console.error("Failed to delete goal", err);
    }
  };

  // Summary totals
  const totalTarget = goals.reduce((a, b) => a + b.target, 0);
  const totalCurrent = goals.reduce((a, b) => a + b.current, 0);
  const overallPct = totalTarget > 0 ? ((totalCurrent / totalTarget) * 100).toFixed(1) : "0";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
            Financial Savings Goals
          </h1>
          <p className="text-sm text-slate-400">
            Define target milestones, track savings progress, and stay motivated.
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={handleOpenAdd}>
          <Plus className="h-4 w-4" />
          <span>Add Savings Goal</span>
        </Button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 sm:gap-4">
        <Card className="p-4 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Active Goals</span>
            <Target className="h-4 w-4 text-teal-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-100">{goals.length}</div>
          <p className="mt-1 text-[11px] text-slate-500">Milestones in progress</p>
        </Card>

        <Card className="p-4 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Target Capital</span>
            <Coins className="h-4 w-4 text-sky-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-100">{formatINR(totalTarget)}</div>
          <p className="mt-1 text-[11px] text-slate-500">Across all active goals</p>
        </Card>

        <Card className="p-4 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Overall Progress</span>
            <Trophy className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-400">{overallPct}%</div>
          <p className="mt-1 text-[11px] text-slate-500">
            {formatINR(totalCurrent)} saved so far
          </p>
        </Card>
      </div>

      {/* Goals Grid */}
      {goals.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center border-slate-800">
          <Target className="h-10 w-10 text-slate-500 mb-2 opacity-50" />
          <h3 className="text-base font-semibold text-slate-200">No savings goals yet</h3>
          <p className="mt-1 text-xs text-slate-400 max-w-sm">
            Create a goal for an emergency fund, vehicle, gadget, or investment portfolio.
          </p>
          <Button variant="primary" size="sm" onClick={handleOpenAdd} className="mt-4">
            <Plus className="h-4 w-4" /> Create First Goal
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {goals.map((goal) => {
            const pct = Math.min((goal.current / (goal.target || 1)) * 100, 100);
            let daysLeft = null;
            if (goal.deadline) {
              const diff = new Date(goal.deadline).getTime() - new Date().getTime();
              daysLeft = Math.ceil(diff / (1000 * 3600 * 24));
            }

            return (
              <Card key={goal.id} className="p-5 border-slate-800 flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-100">{goal.name}</h3>
                      <div className="mt-1 flex items-center gap-2 text-xs text-slate-400">
                        {goal.deadline && (
                          <span className="flex items-center gap-1 text-slate-400">
                            <Calendar className="h-3 w-3" /> Due {formatDate(goal.deadline)}
                          </span>
                        )}
                        {daysLeft !== null && (
                          <span className="flex items-center gap-1 text-teal-400">
                            <Clock className="h-3 w-3" />
                            {daysLeft > 0 ? `${daysLeft} days left` : "Deadline passed"}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleOpenEdit(goal)}
                        className="p-1 text-slate-400 hover:text-teal-400"
                        title="Edit Goal"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setDeletingId(goal.id)}
                        className="p-1 text-slate-400 hover:text-rose-400"
                        title="Delete Goal"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Amounts & Gauge */}
                  <div className="mt-4 flex items-center justify-between">
                    <div>
                      <div className="text-xs text-slate-400">Current Savings</div>
                      <div className="text-xl font-bold text-teal-300">{formatINR(goal.current)}</div>
                      <div className="text-xs text-slate-500">Target: {formatINR(goal.target)}</div>
                    </div>
                    <GoalProgressGauge current={goal.current} target={goal.target} size={110} />
                  </div>

                  {/* Linear Progress Bar */}
                  <div className="mt-2 h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        pct >= 100
                          ? "bg-emerald-400"
                          : pct >= 60
                          ? "bg-teal-400"
                          : "bg-amber-400"
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>

                  {goal.notes && (
                    <p className="mt-3 text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/80">
                      {goal.notes}
                    </p>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Add / Edit Goal Modal */}
      <Modal
        isOpen={isAddModalOpen || editingGoal !== null}
        onClose={() => {
          setIsAddModalOpen(false);
          setEditingGoal(null);
        }}
        title={editingGoal ? "Edit Savings Goal" : "Add New Savings Goal"}
        description="Set a financial milestone to track your accumulated savings."
      >
        <form onSubmit={handleSaveGoal} className="space-y-4">
          <Input
            label="Goal Name *"
            placeholder="e.g. Emergency Fund, MacBook Pro"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Target Amount (₹) *"
              type="number"
              min="1"
              step="500"
              placeholder="100000"
              value={formData.target || ""}
              onChange={(e) =>
                setFormData({ ...formData, target: parseFloat(e.target.value) || 0 })
              }
              required
            />
            <Input
              label="Current Savings (₹)"
              type="number"
              min="0"
              step="500"
              placeholder="25000"
              value={formData.current || ""}
              onChange={(e) =>
                setFormData({ ...formData, current: parseFloat(e.target.value) || 0 })
              }
            />
          </div>

          <Input
            label="Target Deadline"
            type="date"
            value={formData.deadline || ""}
            onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
          />

          <Input
            label="Notes / Description"
            placeholder="e.g. High-yield savings allocation"
            value={formData.notes || ""}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          />

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setIsAddModalOpen(false);
                setEditingGoal(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={formLoading}>
              {editingGoal ? "Save Changes" : "Create Goal"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Goal Modal */}
      <Modal
        isOpen={deletingId !== null}
        onClose={() => setDeletingId(null)}
        title="Delete Savings Goal"
        description="Are you sure you want to remove this goal from your savings tracker?"
      >
        <div className="flex justify-end gap-2 pt-3">
          <Button variant="outline" size="sm" onClick={() => setDeletingId(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => deletingId !== null && handleDeleteGoal(deletingId)}
          >
            Confirm Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}
