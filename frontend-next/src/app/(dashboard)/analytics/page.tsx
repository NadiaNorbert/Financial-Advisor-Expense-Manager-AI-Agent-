"use client";

import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  CreditCard,
  Layers,
  ArrowUpRight,
  PieChart as PieIcon,
  BarChart2,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  CategoryDonutChart,
  MonthlyTrendBarChart,
  DailySpendingLineChart,
} from "@/components/charts/ExpenseCharts";
import { api } from "@/lib/api";
import { formatINR, CATEGORY_COLORS } from "@/lib/utils";
import { SpendingSummary, Expense } from "@/types";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      setLoading(true);
      try {
        const [sum, exp] = await Promise.all([api.getSummary(), api.getExpenses()]);
        setSummary(sum);
        setExpenses(exp);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  const byCategory = summary?.by_category || {};
  const sortedCategories = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);
  const totalSpending = summary?.total_spending || 1;

  // Compute Payment Methods summary
  const paymentMethodStats = React.useMemo(() => {
    const stats: Record<string, { count: number; total: number }> = {};
    expenses.forEach((e) => {
      const pm = e.payment || "Other";
      if (!stats[pm]) stats[pm] = { count: 0, total: 0 };
      stats[pm].count += 1;
      stats[pm].total += e.amount;
    });
    return Object.entries(stats).sort((a, b) => b[1].total - a[1].total);
  }, [expenses]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Spending Analytics
        </h1>
        <p className="text-sm text-slate-400">
          In-depth financial analysis, category breakdown, and historical expenditure trends.
        </p>
      </div>

      {/* Top Categories Metric Tiles */}
      <div>
        <h3 className="mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Top Spending Categories
        </h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
          {sortedCategories.slice(0, 4).map(([cat, amt]) => {
            const pct = (amt / totalSpending) * 100;
            const color = CATEGORY_COLORS[cat] || "#64748B";
            return (
              <Card key={cat} className="p-4 border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400 truncate">{cat}</span>
                  <div
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                </div>
                <div className="mt-2 text-xl font-bold text-slate-100">
                  {formatINR(amt)}
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                  <span>{pct.toFixed(1)}% of total</span>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Charts Row: Category Donut & Monthly History */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-5 p-5 border-slate-800">
          <CardHeader className="mb-2">
            <CardTitle className="text-sm sm:text-base flex items-center gap-2">
              <PieIcon className="h-4 w-4 text-teal-400" />
              Category Allocation
            </CardTitle>
          </CardHeader>
          <CategoryDonutChart byCategory={byCategory} />
        </Card>

        <Card className="lg:col-span-7 p-5 border-slate-800">
          <CardHeader className="mb-2">
            <CardTitle className="text-sm sm:text-base flex items-center gap-2">
              <BarChart2 className="h-4 w-4 text-teal-400" />
              Monthly Expenditure Trend
            </CardTitle>
          </CardHeader>
          <MonthlyTrendBarChart trend={summary?.monthly_trend || []} />
        </Card>
      </div>

      {/* Daily Spending Line Chart */}
      <Card className="p-5 border-slate-800">
        <CardHeader className="mb-2">
          <CardTitle className="text-sm sm:text-base flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-sky-400" />
            Daily Spending Momentum (Last 60 Days)
          </CardTitle>
        </CardHeader>
        <DailySpendingLineChart daily={summary?.daily_spending || []} />
      </Card>

      {/* Detailed Tables: Category Breakdown & Payment Methods */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Category Breakdown Table */}
        <Card className="lg:col-span-7 p-5 border-slate-800">
          <CardHeader className="mb-4">
            <CardTitle className="text-sm sm:text-base flex items-center gap-2">
              <Layers className="h-4 w-4 text-teal-400" />
              Detailed Category Breakdown
            </CardTitle>
          </CardHeader>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                <tr>
                  <th className="pb-2.5">Category</th>
                  <th className="pb-2.5 text-center">Txns</th>
                  <th className="pb-2.5 text-right">Total (₹)</th>
                  <th className="pb-2.5 text-right">Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {sortedCategories.map(([cat, amt]) => {
                  const count = expenses.filter((e) => e.category === cat).length;
                  const pct = (amt / totalSpending) * 100;
                  return (
                    <tr key={cat} className="hover:bg-slate-900/40">
                      <td className="py-2.5 font-medium text-slate-200">{cat}</td>
                      <td className="py-2.5 text-center text-slate-400">{count}</td>
                      <td className="py-2.5 text-right font-bold text-slate-100">
                        {formatINR(amt, 2)}
                      </td>
                      <td className="py-2.5 text-right text-teal-400 font-semibold">
                        {pct.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Payment Methods Breakdown */}
        <Card className="lg:col-span-5 p-5 border-slate-800">
          <CardHeader className="mb-4">
            <CardTitle className="text-sm sm:text-base flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-teal-400" />
              Payment Methods Breakdown
            </CardTitle>
          </CardHeader>

          <div className="space-y-3">
            {paymentMethodStats.map(([method, data]) => {
              const pct = (data.total / totalSpending) * 100;
              return (
                <div key={method} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-slate-200">{method}</span>
                    <span className="text-slate-400">
                      {formatINR(data.total, 2)} ({pct.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-teal-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}
