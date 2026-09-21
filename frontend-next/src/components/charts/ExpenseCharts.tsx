"use client";

import React from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler,
} from "chart.js";
import { Doughnut, Bar, Line } from "react-chartjs-2";
import { CATEGORY_COLORS, formatINR } from "@/lib/utils";

// Register Chart.js modules
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler
);

// ── 1. Category Donut Chart ─────────────────────────────────────────────────

interface DonutChartProps {
  byCategory: Record<string, number>;
}

export function CategoryDonutChart({ byCategory }: DonutChartProps) {
  const labels = Object.keys(byCategory);
  const dataValues = Object.values(byCategory);
  const total = dataValues.reduce((a, b) => a + b, 0);

  if (labels.length === 0 || total === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-slate-500">
        <p className="text-sm">No category spending data yet</p>
      </div>
    );
  }

  const backgroundColors = labels.map(
    (label) => CATEGORY_COLORS[label] || "#64748B"
  );

  const data = {
    labels,
    datasets: [
      {
        data: dataValues,
        backgroundColor: backgroundColors,
        borderColor: "#0f172a",
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right" as const,
        labels: {
          color: "#94a3b8",
          font: { size: 11 },
          padding: 12,
          usePointStyle: true,
          pointStyle: "circle",
        },
      },
      tooltip: {
        backgroundColor: "#1e293b",
        titleColor: "#f8fafc",
        bodyColor: "#38bdf8",
        borderColor: "#334155",
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: function (context: any) {
            const val = context.raw || 0;
            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : "0";
            return ` ${context.label}: ${formatINR(val)} (${pct}%)`;
          },
        },
      },
    },
    cutout: "70%",
  };

  return (
    <div className="relative h-64 w-full">
      <Doughnut data={data} options={options} />
    </div>
  );
}

// ── 2. Monthly Trend Bar Chart ──────────────────────────────────────────────

interface MonthlyBarChartProps {
  trend: Array<{ month: string; amount: number }>;
}

export function MonthlyTrendBarChart({ trend }: MonthlyBarChartProps) {
  if (!trend || trend.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-slate-500">
        <p className="text-sm">Not enough data to display monthly trends</p>
      </div>
    );
  }

  const labels = trend.map((t) => t.month);
  const amounts = trend.map((t) => t.amount);

  const data = {
    labels,
    datasets: [
      {
        label: "Spending (₹)",
        data: amounts,
        backgroundColor: "rgba(20, 184, 166, 0.7)",
        hoverBackgroundColor: "rgba(20, 184, 166, 1)",
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1e293b",
        titleColor: "#f8fafc",
        bodyColor: "#2dd4bf",
        borderColor: "#334155",
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: (ctx: any) => ` Total: ${formatINR(ctx.raw)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: { color: "#94a3b8", font: { size: 11 } },
      },
      y: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "#94a3b8",
          font: { size: 11 },
          callback: (val: any) => `₹${val >= 1000 ? val / 1000 + "k" : val}`,
        },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Bar data={data} options={options} />
    </div>
  );
}

// ── 3. Daily Spending Line Chart ────────────────────────────────────────────

interface DailyLineChartProps {
  daily: Array<{ date: string; amount: number }>;
}

export function DailySpendingLineChart({ daily }: DailyLineChartProps) {
  if (!daily || daily.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-slate-500">
        <p className="text-sm">No daily spending records yet</p>
      </div>
    );
  }

  const labels = daily.map((d) => d.date.slice(5)); // MM-DD
  const amounts = daily.map((d) => d.amount);

  const data = {
    labels,
    datasets: [
      {
        label: "Daily Spend",
        data: amounts,
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56, 189, 248, 0.12)",
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#0284c7",
        pointBorderColor: "#38bdf8",
        pointRadius: 3,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1e293b",
        titleColor: "#f8fafc",
        bodyColor: "#38bdf8",
        borderColor: "#334155",
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: (ctx: any) => ` Spent: ${formatINR(ctx.raw)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(255, 255, 255, 0.04)" },
        ticks: { color: "#94a3b8", font: { size: 10 }, maxTicksLimit: 12 },
      },
      y: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "#94a3b8",
          font: { size: 11 },
          callback: (val: any) => `₹${val >= 1000 ? val / 1000 + "k" : val}`,
        },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Line data={data} options={options} />
    </div>
  );
}

// ── 4. Budget vs Actual Bar Chart ───────────────────────────────────────────

interface BudgetVsActualProps {
  categories: Array<{ category: string; budget: number; spent: number }>;
}

export function BudgetVsActualChart({ categories }: BudgetVsActualProps) {
  const active = categories.filter((c) => c.budget > 0 || c.spent > 0);
  if (active.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-slate-500">
        <p className="text-sm">No budget allocations set</p>
      </div>
    );
  }

  const labels = active.map((c) => c.category);
  const budgets = active.map((c) => c.budget);
  const spents = active.map((c) => c.spent);

  const data = {
    labels,
    datasets: [
      {
        label: "Planned Budget",
        data: budgets,
        backgroundColor: "rgba(59, 130, 246, 0.6)",
        borderRadius: 4,
      },
      {
        label: "Actual Spent",
        data: spents,
        backgroundColor: spents.map((s, i) =>
          s > budgets[i] && budgets[i] > 0
            ? "rgba(239, 68, 68, 0.8)"
            : "rgba(16, 185, 129, 0.8)"
        ),
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: { color: "#94a3b8", font: { size: 11 }, usePointStyle: true },
      },
      tooltip: {
        backgroundColor: "#1e293b",
        titleColor: "#f8fafc",
        borderColor: "#334155",
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.dataset.label}: ${formatINR(ctx.raw)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: { color: "#94a3b8", font: { size: 10 } },
      },
      y: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "#94a3b8",
          font: { size: 11 },
          callback: (val: any) => `₹${val >= 1000 ? val / 1000 + "k" : val}`,
        },
      },
    },
  };

  return (
    <div className="h-72 w-full">
      <Bar data={data} options={options} />
    </div>
  );
}

// ── 5. Goal Progress Gauge ──────────────────────────────────────────────────

interface GoalGaugeProps {
  current: number;
  target: number;
  size?: number;
}

export function GoalProgressGauge({ current, target, size = 120 }: GoalGaugeProps) {
  const pct = Math.min(Math.round((current / (target || 1)) * 100), 100);
  const remaining = Math.max(0, 100 - pct);

  const data = {
    datasets: [
      {
        data: [pct, remaining],
        backgroundColor: [
          pct >= 100 ? "#10B981" : pct >= 60 ? "#14B8A6" : "#F59E0B",
          "rgba(255, 255, 255, 0.06)",
        ],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
    },
    cutout: "75%",
    rotation: -90,
    circumference: 180,
  };

  return (
    <div className="relative flex flex-col items-center" style={{ width: size, height: size * 0.65 }}>
      <div className="h-full w-full">
        <Doughnut data={data} options={options} />
      </div>
      <div className="absolute bottom-0 text-center">
        <span className="text-sm font-bold text-slate-100">{pct}%</span>
      </div>
    </div>
  );
}
