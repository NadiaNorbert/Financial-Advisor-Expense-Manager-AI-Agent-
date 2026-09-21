"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  FileSpreadsheet,
  Download,
  Receipt,
  PieChart as PieIcon,
  Target,
  ShieldCheck,
  Eye,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { formatINR, formatDate } from "@/lib/utils";
import { Expense, SpendingSummary, BudgetCalculation, Goal } from "@/types";

export default function ReportsPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [budgetData, setBudgetData] = useState<BudgetCalculation | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [activePreview, setActiveTab] = useState<"expenses" | "budget" | "goals" | "txt">("expenses");

  useEffect(() => {
    async function loadData() {
      try {
        const [exp, sum, bud, gls] = await Promise.all([
          api.getExpenses(),
          api.getSummary(),
          api.getBudgetCalculation(),
          api.getGoals(),
        ]);
        setExpenses(exp);
        setSummary(sum);
        setBudgetData(bud);
        setGoals(gls);
      } catch (err) {
        console.error("Failed to load reports data", err);
      }
    }
    loadData();
  }, []);

  const downloadReport = (type: "expenses" | "budget" | "goals" | "summary") => {
    const today = new Date().toISOString().split("T")[0];
    let content = "";
    let mimeType = "text/csv";
    let filename = `finmate_${type}_${today}.csv`;

    if (type === "expenses") {
      content =
        "Date,Merchant,Category,Amount,Payment,Source,Notes\n" +
        expenses
          .map(
            (e) =>
              `"${e.date}","${e.merchant.replace(/"/g, '""')}","${e.category}",${e.amount},"${e.payment}","${e.source || "manual"}","${(e.notes || "").replace(/"/g, '""')}"`
          )
          .join("\n");
    } else if (type === "budget") {
      content =
        "Category,Budget,Spent,Remaining,Utilization%,Status\n" +
        (budgetData?.by_category || [])
          .map(
            (c) =>
              `"${c.category}",${c.budget},${c.spent},${c.remaining},${c.pct}%,"${c.over_budget ? "OVER BUDGET" : "ON TRACK"}"`
          )
          .join("\n");
    } else if (type === "goals") {
      content =
        "Goal,Target,Current,Progress%,Deadline,Notes\n" +
        goals
          .map(
            (g) =>
              `"${g.name}",${g.target},${g.current},${((g.current / (g.target || 1)) * 100).toFixed(1)}%,"${g.deadline || ""}","${(g.notes || "").replace(/"/g, '""')}"`
          )
          .join("\n");
    } else if (type === "summary") {
      mimeType = "text/plain";
      filename = `finmate_summary_${today}.txt`;
      content = `========================================================
FINMATE AI - FINANCIAL SUMMARY REPORT
Generated: ${new Date().toLocaleString("en-IN")}
========================================================

SPENDING OVERVIEW:
--------------------------------------------------------
Total Expenditure  : ${formatINR(summary?.total_spending || 0)}
Monthly Expenditure: ${formatINR(summary?.monthly_spending || 0)}
Total Transactions : ${summary?.transaction_count || 0}
Top Category       : ${summary?.top_category || "N/A"}

BUDGET STATUS:
--------------------------------------------------------
Monthly Income     : ${formatINR(budgetData?.income || 0)}
Total Budget       : ${formatINR(budgetData?.total_budget || 0)}
Total Spent        : ${formatINR(budgetData?.total_spent || 0)}
Remaining Budget   : ${formatINR(budgetData?.remaining || 0)}
Estimated Savings  : ${formatINR(budgetData?.savings_estimate || 0)}

SAVINGS GOALS:
--------------------------------------------------------
${goals.map((g) => `- ${g.name}: ${formatINR(g.current)} / ${formatINR(g.target)} (${((g.current / (g.target || 1)) * 100).toFixed(0)}%) | Due: ${g.deadline || "N/A"}`).join("\n")}

========================================================
DISCLAIMER: This report is for personal financial tracking only.
`;
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Financial Reports & Export
        </h1>
        <p className="text-sm text-slate-400">
          Generate, preview, and download comprehensive financial summaries in CSV and TXT formats.
        </p>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
        <Card className="p-4 border-slate-800">
          <span className="text-xs text-slate-400">Total Spent</span>
          <div className="mt-1.5 text-xl font-bold text-slate-100">
            {formatINR(summary?.total_spending || 0)}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">All-time recorded</p>
        </Card>

        <Card className="p-4 border-slate-800">
          <span className="text-xs text-slate-400">Transactions</span>
          <div className="mt-1.5 text-xl font-bold text-teal-400">
            {summary?.transaction_count || 0}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Total entries</p>
        </Card>

        <Card className="p-4 border-slate-800">
          <span className="text-xs text-slate-400">Categories</span>
          <div className="mt-1.5 text-xl font-bold text-sky-400">
            {Object.keys(summary?.by_category || {}).length}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Active spending buckets</p>
        </Card>

        <Card className="p-4 border-slate-800">
          <span className="text-xs text-slate-400">Active Goals</span>
          <div className="mt-1.5 text-xl font-bold text-emerald-400">
            {goals.length}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Savings targets</p>
        </Card>
      </div>

      {/* Export Cards Grid */}
      <div>
        <h3 className="mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Download Reports
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Card 1: Expenses CSV */}
          <Card className="p-5 border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
                  <FileSpreadsheet className="h-5 w-5" />
                </div>
                <Badge variant="teal">CSV</Badge>
              </div>
              <h4 className="mt-3 text-sm font-bold text-slate-100">Expenses Log</h4>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                Complete transaction records including date, merchant, amount, category, and payment method.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadReport("expenses")}
              className="w-full"
            >
              <Download className="h-4 w-4" /> Download CSV
            </Button>
          </Card>

          {/* Card 2: Budget CSV */}
          <Card className="p-5 border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                  <PieIcon className="h-5 w-5" />
                </div>
                <Badge variant="blue">CSV</Badge>
              </div>
              <h4 className="mt-3 text-sm font-bold text-slate-100">Budget Report</h4>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                Category-wise budget allocations vs actual spending, utilization percentages, and status.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadReport("budget")}
              className="w-full"
            >
              <Download className="h-4 w-4" /> Download CSV
            </Button>
          </Card>

          {/* Card 3: Goals CSV */}
          <Card className="p-5 border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                  <Target className="h-5 w-5" />
                </div>
                <Badge variant="purple">CSV</Badge>
              </div>
              <h4 className="mt-3 text-sm font-bold text-slate-100">Savings Goals</h4>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                All financial goals with target amounts, accumulated savings, progress percentages, and deadlines.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadReport("goals")}
              className="w-full"
            >
              <Download className="h-4 w-4" /> Download CSV
            </Button>
          </Card>

          {/* Card 4: Summary TXT */}
          <Card className="p-5 border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <FileText className="h-5 w-5" />
                </div>
                <Badge variant="green">TXT</Badge>
              </div>
              <h4 className="mt-3 text-sm font-bold text-slate-100">Full Summary</h4>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                Comprehensive plain-text financial dossier containing all expenses, budget status, and goals.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadReport("summary")}
              className="w-full"
            >
              <Download className="h-4 w-4" /> Download TXT
            </Button>
          </Card>
        </div>
      </div>

      {/* On-Screen Preview Tabs */}
      <Card className="p-5 border-slate-800 space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Eye className="h-4 w-4 text-teal-400" />
            Live Report Preview
          </CardTitle>

          <div className="flex rounded-lg border border-slate-800 bg-slate-950 p-0.5 text-xs">
            <button
              onClick={() => setActiveTab("expenses")}
              className={`rounded px-3 py-1 font-medium transition-colors ${
                activePreview === "expenses" ? "bg-slate-800 text-teal-300 font-bold" : "text-slate-400"
              }`}
            >
              Expenses
            </button>
            <button
              onClick={() => setActiveTab("budget")}
              className={`rounded px-3 py-1 font-medium transition-colors ${
                activePreview === "budget" ? "bg-slate-800 text-teal-300 font-bold" : "text-slate-400"
              }`}
            >
              Budget
            </button>
            <button
              onClick={() => setActiveTab("goals")}
              className={`rounded px-3 py-1 font-medium transition-colors ${
                activePreview === "goals" ? "bg-slate-800 text-teal-300 font-bold" : "text-slate-400"
              }`}
            >
              Goals
            </button>
          </div>
        </div>

        {/* Preview Content */}
        {activePreview === "expenses" && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                <tr>
                  <th className="py-2.5">Date</th>
                  <th className="py-2.5">Merchant</th>
                  <th className="py-2.5">Category</th>
                  <th className="py-2.5 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {expenses.slice(0, 8).map((e) => (
                  <tr key={e.id} className="hover:bg-slate-900/40">
                    <td className="py-2.5 text-slate-400">{e.date}</td>
                    <td className="py-2.5 font-medium text-slate-200">{e.merchant}</td>
                    <td className="py-2.5 text-slate-400">{e.category}</td>
                    <td className="py-2.5 text-right font-bold text-slate-100">{formatINR(e.amount, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activePreview === "budget" && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                <tr>
                  <th className="py-2.5">Category</th>
                  <th className="py-2.5 text-right">Budget</th>
                  <th className="py-2.5 text-right">Spent</th>
                  <th className="py-2.5 text-right">Usage</th>
                  <th className="py-2.5 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(budgetData?.by_category || []).map((c) => (
                  <tr key={c.category} className="hover:bg-slate-900/40">
                    <td className="py-2.5 font-medium text-slate-200">{c.category}</td>
                    <td className="py-2.5 text-right text-slate-400">{formatINR(c.budget)}</td>
                    <td className="py-2.5 text-right text-slate-300">{formatINR(c.spent)}</td>
                    <td className="py-2.5 text-right text-teal-400 font-semibold">{c.pct.toFixed(0)}%</td>
                    <td className="py-2.5 text-right">
                      <Badge variant={c.over_budget ? "red" : "green"}>
                        {c.over_budget ? "Over" : "OK"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activePreview === "goals" && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                <tr>
                  <th className="py-2.5">Goal Name</th>
                  <th className="py-2.5 text-right">Target</th>
                  <th className="py-2.5 text-right">Saved</th>
                  <th className="py-2.5 text-right">Progress</th>
                  <th className="py-2.5 text-right">Deadline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {goals.map((g) => {
                  const pct = ((g.current / (g.target || 1)) * 100).toFixed(0);
                  return (
                    <tr key={g.id} className="hover:bg-slate-900/40">
                      <td className="py-2.5 font-medium text-slate-200">{g.name}</td>
                      <td className="py-2.5 text-right text-slate-400">{formatINR(g.target)}</td>
                      <td className="py-2.5 text-right text-teal-300 font-bold">{formatINR(g.current)}</td>
                      <td className="py-2.5 text-right text-emerald-400 font-semibold">{pct}%</td>
                      <td className="py-2.5 text-right text-slate-400">{g.deadline || "N/A"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Privacy Notice */}
      <div className="flex items-center gap-2 rounded-xl bg-slate-900/40 border border-slate-800 p-3.5 text-xs text-slate-400">
        <ShieldCheck className="h-4 w-4 text-teal-400 shrink-0" />
        <span>
          <strong>Data Privacy:</strong> All report generation and financial data processing is performed securely on your local environment without unencrypted external cloud exposure.
        </span>
      </div>
    </div>
  );
}
