"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  TrendingUp,
  Calendar,
  Wallet,
  Receipt,
  Trophy,
  ArrowUpRight,
  ArrowRight,
  ScanLine,
  PlusCircle,
  Sparkles,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  CategoryDonutChart,
  MonthlyTrendBarChart,
  DailySpendingLineChart,
} from "@/components/charts/ExpenseCharts";
import { api } from "@/lib/api";
import { formatINR, formatDate, formatRelativeDate } from "@/lib/utils";
import { SpendingSummary, BudgetCalculation, Expense } from "@/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [budgetData, setBudgetData] = useState<BudgetCalculation | null>(null);
  const [recentExpenses, setRecentExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      setLoading(true);
      try {
        const [sum, bud, exp] = await Promise.all([
          api.getSummary(),
          api.getBudgetCalculation(),
          api.getExpenses({ limit: 8 } as any),
        ]);
        setSummary(sum);
        setBudgetData(bud);
        setRecentExpenses(exp.slice(0, 6));
      } catch (err) {
        console.error("Error loading dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const totalBudget = budgetData?.total_budget || 0;
  const monthlySpent = summary?.monthly_spending || 0;
  const budgetPct = totalBudget > 0 ? Math.min((monthlySpent / totalBudget) * 100, 100) : 0;
  const isOverBudget = totalBudget > 0 && monthlySpent > totalBudget;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
            Financial Dashboard
          </h1>
          <p className="text-sm text-slate-400">
            Real-time overview of your income, expenses, budgets, and savings.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/upload">
            <Button size="sm" variant="primary">
              <ScanLine className="h-4 w-4" />
              <span>Scan Receipt</span>
            </Button>
          </Link>
          <Link href="/expenses">
            <Button size="sm" variant="outline">
              <PlusCircle className="h-4 w-4" />
              <span>Add Expense</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 lg:grid-cols-5 sm:gap-4">
        {/* KPI 1: Total Spending */}
        <Card className="p-4 bg-gradient-to-br from-slate-900 to-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Spent</span>
            <div className="rounded-lg bg-teal-500/10 p-1.5 text-teal-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100 sm:text-2xl">
            {formatINR(summary?.total_spending || 0)}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">All-time recorded</p>
        </Card>

        {/* KPI 2: This Month */}
        <Card className="p-4 bg-gradient-to-br from-slate-900 to-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">This Month</span>
            <div className="rounded-lg bg-blue-500/10 p-1.5 text-blue-400">
              <Calendar className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100 sm:text-2xl">
            {formatINR(summary?.monthly_spending || 0)}
          </div>
          <p className="mt-1 text-[11px] text-teal-400">Current cycle</p>
        </Card>

        {/* KPI 3: Remaining Budget */}
        <Card className="p-4 bg-gradient-to-br from-slate-900 to-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Remaining Budget</span>
            <div className="rounded-lg bg-emerald-500/10 p-1.5 text-emerald-400">
              <Wallet className="h-4 w-4" />
            </div>
          </div>
          <div
            className={`mt-2 text-xl font-bold sm:text-2xl ${
              isOverBudget ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {formatINR(budgetData?.remaining || 0)}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            of {formatINR(totalBudget)} budget
          </p>
        </Card>

        {/* KPI 4: Transactions */}
        <Card className="p-4 bg-gradient-to-br from-slate-900 to-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Transactions</span>
            <div className="rounded-lg bg-purple-500/10 p-1.5 text-purple-400">
              <Receipt className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100 sm:text-2xl">
            {summary?.transaction_count || 0}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Total entries</p>
        </Card>

        {/* KPI 5: Top Category */}
        <Card className="col-span-2 sm:col-span-1 p-4 bg-gradient-to-br from-slate-900 to-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Top Category</span>
            <div className="rounded-lg bg-amber-500/10 p-1.5 text-amber-400">
              <Trophy className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 truncate text-lg font-bold text-amber-300 sm:text-xl">
            {summary?.top_category || "N/A"}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Highest category spend</p>
        </Card>
      </div>

      {/* Monthly Budget Health Progress Bar */}
      {totalBudget > 0 && (
        <Card className="p-4 sm:p-5 border-slate-800">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm sm:text-base text-slate-200">
                Monthly Budget Health
              </span>
              {isOverBudget ? (
                <Badge variant="red">
                  <AlertTriangle className="h-3 w-3" /> Over Budget
                </Badge>
              ) : budgetPct > 80 ? (
                <Badge variant="yellow">Near Limit</Badge>
              ) : (
                <Badge variant="green">
                  <CheckCircle2 className="h-3 w-3" /> On Track
                </Badge>
              )}
            </div>
            <span className="text-xs font-semibold text-slate-300">
              {budgetPct.toFixed(1)}% used ({formatINR(monthlySpent)} / {formatINR(totalBudget)})
            </span>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                isOverBudget
                  ? "bg-rose-500"
                  : budgetPct > 80
                  ? "bg-amber-500"
                  : "bg-gradient-to-r from-teal-500 to-emerald-400"
              }`}
              style={{ width: `${budgetPct}%` }}
            />
          </div>
        </Card>
      )}

      {/* Visualizations Row 1: Donut & Monthly Trend */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Category Spending Donut */}
        <Card className="lg:col-span-5 p-5">
          <CardHeader className="mb-2">
            <div>
              <CardTitle>Spending by Category</CardTitle>
              <p className="text-xs text-slate-400">All-time category distribution</p>
            </div>
            <Link href="/analytics" className="text-xs font-medium text-teal-400 hover:text-teal-300 flex items-center gap-1">
              Details <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </CardHeader>
          <CategoryDonutChart byCategory={summary?.by_category || {}} />
        </Card>

        {/* Monthly Spending Trend Bar */}
        <Card className="lg:col-span-7 p-5">
          <CardHeader className="mb-2">
            <div>
              <CardTitle>Monthly Spending History</CardTitle>
              <p className="text-xs text-slate-400">Total expenditure month by month</p>
            </div>
            <Link href="/analytics" className="text-xs font-medium text-teal-400 hover:text-teal-300 flex items-center gap-1">
              Analytics <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </CardHeader>
          <MonthlyTrendBarChart trend={summary?.monthly_trend || []} />
        </Card>
      </div>

      {/* Spending Trend Line Chart */}
      <Card className="p-5">
        <CardHeader className="mb-2">
          <div>
            <CardTitle>Daily Spending Momentum</CardTitle>
            <p className="text-xs text-slate-400">Daily transaction volume across recent weeks</p>
          </div>
        </CardHeader>
        <DailySpendingLineChart daily={summary?.daily_spending || []} />
      </Card>

      {/* Recent Transactions & Quick Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Recent Transactions List */}
        <Card className="lg:col-span-8 p-5">
          <CardHeader className="mb-4">
            <CardTitle>Recent Transactions</CardTitle>
            <Link href="/expenses" className="text-xs font-medium text-teal-400 hover:text-teal-300 flex items-center gap-1">
              View All <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardHeader>

          {recentExpenses.length === 0 ? (
            <div className="py-8 text-center text-slate-500">
              <p className="text-sm">No recent transactions recorded</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800/80">
              {recentExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between py-3 transition-colors hover:bg-slate-900/40 rounded-lg px-2"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-800 text-teal-400 text-xs font-bold border border-slate-700/60">
                      {expense.category.charAt(0)}
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-200">
                        {expense.merchant}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span>{formatRelativeDate(expense.date)}</span>
                        <span>•</span>
                        <span className="text-slate-500">{expense.category}</span>
                        <span>•</span>
                        <span className="text-teal-400/80">{expense.payment}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-slate-100">
                      -{formatINR(expense.amount, 2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Quick Actions Panel */}
        <Card className="lg:col-span-4 p-5 flex flex-col justify-between">
          <CardHeader className="mb-3">
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>

          <div className="space-y-2.5">
            <Link href="/upload" className="block">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-teal-500/30 hover:bg-slate-900/80 transition-all group">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
                    <ScanLine className="h-4 w-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-slate-200 group-hover:text-teal-300">
                      Scan Payment Receipt
                    </h5>
                    <p className="text-[11px] text-slate-500">Auto-extract with OCR</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-teal-400 transition-colors" />
              </div>
            </Link>

            <Link href="/advisor" className="block">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-teal-500/30 hover:bg-slate-900/80 transition-all group">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-slate-200 group-hover:text-purple-300">
                      AI Financial Advisor
                    </h5>
                    <p className="text-[11px] text-slate-500">Buffett, Kiyosaki & Ramit</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-purple-400 transition-colors" />
              </div>
            </Link>

            <Link href="/budget" className="block">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-teal-500/30 hover:bg-slate-900/80 transition-all group">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                    <Wallet className="h-4 w-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-slate-200 group-hover:text-blue-300">
                      Manage Budgets
                    </h5>
                    <p className="text-[11px] text-slate-500">Set category spending limits</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-blue-400 transition-colors" />
              </div>
            </Link>

            <Link href="/reports" className="block">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-teal-500/30 hover:bg-slate-900/80 transition-all group">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                    <FileSpreadsheet className="h-4 w-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-slate-200 group-hover:text-emerald-300">
                      Export Financial Reports
                    </h5>
                    <p className="text-[11px] text-slate-500">Download CSV & TXT</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-emerald-400 transition-colors" />
              </div>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
