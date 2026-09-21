"use client";

import React, { useState, useEffect } from "react";
import {
  Wallet,
  PieChart as PieIcon,
  Settings,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingDown,
  Save,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { BudgetVsActualChart } from "@/components/charts/ExpenseCharts";
import { api } from "@/lib/api";
import { formatINR, CATEGORIES } from "@/lib/utils";
import { BudgetCalculation, BudgetSettings } from "@/types";

export default function BudgetPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "settings">("overview");
  const [budgetData, setBudgetData] = useState<BudgetCalculation | null>(null);
  const [loading, setLoading] = useState(true);

  // Settings form state
  const [income, setIncome] = useState<number>(65000);
  const [categoryBudgets, setCategoryBudgets] = useState<Record<string, number>>({});
  const [savingSettings, setSavingSettings] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadBudgetData();
  }, []);

  async function loadBudgetData() {
    setLoading(true);
    try {
      const [calc, settings] = await Promise.all([
        api.getBudgetCalculation(),
        api.getBudgetSettings(),
      ]);
      setBudgetData(calc);
      setIncome(settings.income);
      setCategoryBudgets(settings.budgets);
    } catch (err) {
      console.error("Failed to load budget data", err);
    } finally {
      setLoading(false);
    }
  }

  const handleSaveBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSettings(true);
    try {
      await api.saveBudgetSettings(income, categoryBudgets);
      setSaveSuccess(true);
      await loadBudgetData();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save budget settings", err);
    } finally {
      setSavingSettings(false);
    }
  };

  const totalAllocated = Object.values(categoryBudgets).reduce((a, b) => a + (b || 0), 0);
  const unallocated = income - totalAllocated;

  const totalBudget = budgetData?.total_budget || 0;
  const totalSpent = budgetData?.total_spent || 0;
  const overallPct = totalBudget > 0 ? Math.min((totalSpent / totalBudget) * 100, 100) : 0;
  const isOverBudget = totalBudget > 0 && totalSpent > totalBudget;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Budget Planning & Management
        </h1>
        <p className="text-sm text-slate-400">
          Set category-wise monthly spending limits, monitor consumption, and prevent overspending.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "overview"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <PieIcon className="h-4 w-4" />
          <span>Budget Overview</span>
        </button>
        <button
          onClick={() => setActiveTab("settings")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "settings"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Settings className="h-4 w-4" />
          <span>Configure Budget Settings</span>
        </button>
      </div>

      {/* ── TAB 1: Budget Overview ──────────────────────────────────── */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
            <Card className="p-4 border-slate-800">
              <span className="text-xs text-slate-400">Monthly Income</span>
              <div className="mt-1.5 text-xl font-bold text-slate-100 sm:text-2xl">
                {formatINR(budgetData?.income || 0)}
              </div>
              <p className="mt-1 text-[11px] text-teal-400">Take-home salary</p>
            </Card>

            <Card className="p-4 border-slate-800">
              <span className="text-xs text-slate-400">Total Budgeted</span>
              <div className="mt-1.5 text-xl font-bold text-slate-100 sm:text-2xl">
                {formatINR(totalBudget)}
              </div>
              <p className="mt-1 text-[11px] text-slate-500">Planned allocations</p>
            </Card>

            <Card className="p-4 border-slate-800">
              <span className="text-xs text-slate-400">Remaining Budget</span>
              <div
                className={`mt-1.5 text-xl font-bold sm:text-2xl ${
                  isOverBudget ? "text-rose-400" : "text-emerald-400"
                }`}
              >
                {formatINR(budgetData?.remaining || 0)}
              </div>
              <p className="mt-1 text-[11px] text-slate-500">Available to spend</p>
            </Card>

            <Card className="p-4 border-slate-800">
              <span className="text-xs text-slate-400">Estimated Savings</span>
              <div className="mt-1.5 text-xl font-bold text-sky-400 sm:text-2xl">
                {formatINR(budgetData?.savings_estimate || 0)}
              </div>
              <p className="mt-1 text-[11px] text-slate-500">Income - actual spending</p>
            </Card>
          </div>

          {/* Overall Health Card */}
          {totalBudget > 0 && (
            <Card className="p-5 border-slate-800">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-3">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-sm sm:text-base text-slate-200">
                    Overall Budget Consumption
                  </h3>
                  {isOverBudget ? (
                    <Badge variant="red">
                      <AlertTriangle className="h-3 w-3" /> Over Budget
                    </Badge>
                  ) : overallPct > 80 ? (
                    <Badge variant="yellow">Near Limit</Badge>
                  ) : (
                    <Badge variant="green">
                      <CheckCircle2 className="h-3 w-3" /> On Track
                    </Badge>
                  )}
                </div>
                <span className="text-xs font-semibold text-slate-300">
                  {overallPct.toFixed(1)}% utilized ({formatINR(totalSpent)} / {formatINR(totalBudget)})
                </span>
              </div>
              <div className="h-3.5 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isOverBudget
                      ? "bg-rose-500"
                      : overallPct > 80
                      ? "bg-amber-500"
                      : "bg-gradient-to-r from-teal-500 to-emerald-400"
                  }`}
                  style={{ width: `${overallPct}%` }}
                />
              </div>
            </Card>
          )}

          {/* Category Progress Bars Grid */}
          <div>
            <h3 className="mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Category Budget Status
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {budgetData?.by_category
                .filter((c) => c.budget > 0 || c.spent > 0)
                .map((item) => {
                  const pct = item.budget > 0 ? Math.min((item.spent / item.budget) * 100, 100) : 0;
                  const isOver = item.spent > item.budget && item.budget > 0;
                  return (
                    <Card key={item.category} className="p-4 border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm text-slate-200">{item.category}</span>
                        {isOver ? (
                          <Badge variant="red">Over by {formatINR(Math.abs(item.remaining))}</Badge>
                        ) : (
                          <span className="text-xs font-semibold text-teal-400">
                            {item.pct.toFixed(0)}%
                          </span>
                        )}
                      </div>

                      <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            isOver ? "bg-rose-500" : pct > 80 ? "bg-amber-500" : "bg-teal-400"
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>{formatINR(item.spent)} spent</span>
                        <span>{formatINR(item.budget)} budget</span>
                      </div>
                    </Card>
                  );
                })}
            </div>
          </div>

          {/* Budget vs Actual Visualization Chart */}
          <Card className="p-5 border-slate-800">
            <CardHeader className="mb-3">
              <CardTitle>Planned Budget vs Actual Expenditure</CardTitle>
            </CardHeader>
            <BudgetVsActualChart categories={budgetData?.by_category || []} />
          </Card>
        </div>
      )}

      {/* ── TAB 2: Budget Settings ──────────────────────────────────── */}
      {activeTab === "settings" && (
        <Card className="max-w-3xl mx-auto p-6 border-slate-800">
          <CardHeader className="mb-4">
            <div>
              <CardTitle>Configure Monthly Budget Allocations</CardTitle>
              <p className="text-xs text-slate-400">
                Specify your take-home income and allocate spending limits for each category.
              </p>
            </div>
          </CardHeader>

          {saveSuccess && (
            <div className="mb-4 flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Budget settings saved and updated in database!</span>
            </div>
          )}

          <form onSubmit={handleSaveBudget} className="space-y-6">
            {/* Income Input */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <Input
                label="Monthly Take-Home Income (₹) *"
                type="number"
                min="0"
                step="500"
                value={income || ""}
                onChange={(e) => setIncome(parseFloat(e.target.value) || 0)}
                placeholder="65000"
                required
              />
            </div>

            {/* Category Allocations Grid */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Category Spending Allocations (₹)
              </h4>
              <p className="text-xs text-slate-500">Leave at 0 to leave untracked</p>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {CATEGORIES.map((cat) => (
                  <Input
                    key={cat}
                    label={cat}
                    type="number"
                    min="0"
                    step="100"
                    value={categoryBudgets[cat] ?? 0}
                    onChange={(e) =>
                      setCategoryBudgets({
                        ...categoryBudgets,
                        [cat]: parseFloat(e.target.value) || 0,
                      })
                    }
                  />
                ))}
              </div>
            </div>

            {/* Live Calculation Summary Box */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-2 text-xs">
              <div className="flex justify-between text-slate-300">
                <span>Monthly Income:</span>
                <strong className="text-slate-100">{formatINR(income)}</strong>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Total Planned Allocations:</span>
                <strong className="text-slate-100">{formatINR(totalAllocated)}</strong>
              </div>
              <div
                className={`flex justify-between border-t border-slate-800 pt-2 font-bold ${
                  unallocated >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                <span>Unallocated Capital (Savings):</span>
                <span>{formatINR(unallocated)}</span>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={savingSettings}
            >
              <Save className="h-4 w-4" /> Save Budget Configuration
            </Button>
          </form>
        </Card>
      )}
    </div>
  );
}
