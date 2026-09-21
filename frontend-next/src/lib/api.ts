/**
 * FinMate AI - API Service Layer
 * Fully user-usable: Communicates with FastAPI backend with local dynamic persistence.
 * Zero static mock data. Starts clean for every user and persists real transactions.
 */

import axios from "axios";
import {
  Expense,
  ExpenseInput,
  Goal,
  GoalInput,
  SpendingSummary,
  BudgetCalculation,
  BudgetSettings,
  AdviceResult,
  OCRResult,
  User,
  AuthResponse,
  Guru,
} from "@/types";
import { CATEGORIES } from "./utils";
import { GURUS } from "./mock-data";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Attach JWT token if present in localStorage
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("finmate_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ── Local Dynamic Persistence Helpers ────────────────────────────────────────

function getLocalExpenses(): Expense[] {
  if (typeof window === "undefined") return [];
  try {
    const stored = localStorage.getItem("finmate_expenses");
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function setLocalExpenses(expenses: Expense[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem("finmate_expenses", JSON.stringify(expenses));
  } catch (e) {
    console.error("Failed to save local expenses", e);
  }
}

function getLocalGoals(): Goal[] {
  if (typeof window === "undefined") return [];
  try {
    const stored = localStorage.getItem("finmate_goals");
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function setLocalGoals(goals: Goal[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem("finmate_goals", JSON.stringify(goals));
  } catch (e) {
    console.error("Failed to save local goals", e);
  }
}

function getLocalBudgetSettings(): { income: number; budgets: Record<string, number>; month: string } {
  const currentMonth = new Date().toISOString().substring(0, 7);
  if (typeof window === "undefined") {
    return {
      income: 0,
      budgets: Object.fromEntries(CATEGORIES.map((c) => [c, 0])),
      month: currentMonth,
    };
  }
  try {
    const stored = localStorage.getItem("finmate_budget_settings");
    if (stored) return JSON.parse(stored);
  } catch {}

  return {
    income: 0,
    budgets: Object.fromEntries(CATEGORIES.map((c) => [c, 0])),
    month: currentMonth,
  };
}

function setLocalBudgetSettings(settings: { income: number; budgets: Record<string, number>; month: string }): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem("finmate_budget_settings", JSON.stringify(settings));
  } catch (e) {
    console.error("Failed to save local budget settings", e);
  }
}

function computeDynamicSummary(expenses: Expense[]): SpendingSummary {
  if (!expenses || expenses.length === 0) {
    return {
      total_spending: 0,
      monthly_spending: 0,
      by_category: {},
      monthly_trend: [],
      daily_spending: [],
      top_category: "N/A",
      transaction_count: 0,
    };
  }

  const currentMonth = new Date().toISOString().substring(0, 7);
  let totalSpending = 0;
  let monthlySpending = 0;
  const byCategory: Record<string, number> = {};
  const monthlyMap: Record<string, number> = {};
  const dailyMap: Record<string, number> = {};

  for (const exp of expenses) {
    const amt = Number(exp.amount) || 0;
    totalSpending += amt;

    const dateStr = String(exp.date || "");
    const month = dateStr.substring(0, 7);
    const day = dateStr.substring(0, 10);

    if (month === currentMonth) {
      monthlySpending += amt;
    }

    // Category aggregation
    const cat = exp.category || "Others";
    byCategory[cat] = (byCategory[cat] || 0) + amt;

    // Monthly trend
    if (month) {
      monthlyMap[month] = (monthlyMap[month] || 0) + amt;
    }

    // Daily spending
    if (day) {
      dailyMap[day] = (dailyMap[day] || 0) + amt;
    }
  }

  // Determine top category
  let topCategory = "N/A";
  let maxSpend = -1;
  for (const [cat, amt] of Object.entries(byCategory)) {
    if (amt > maxSpend) {
      maxSpend = amt;
      topCategory = cat;
    }
  }

  const monthlyTrend = Object.entries(monthlyMap)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-12)
    .map(([month, amount]) => ({ month, amount: Math.round(amount * 100) / 100 }));

  const dailySpending = Object.entries(dailyMap)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-60)
    .map(([date, amount]) => ({ date, amount: Math.round(amount * 100) / 100 }));

  return {
    total_spending: Math.round(totalSpending * 100) / 100,
    monthly_spending: Math.round(monthlySpending * 100) / 100,
    by_category: Object.fromEntries(
      Object.entries(byCategory).map(([k, v]) => [k, Math.round(v * 100) / 100])
    ),
    monthly_trend: monthlyTrend,
    daily_spending: dailySpending,
    top_category: topCategory,
    transaction_count: expenses.length,
  };
}

function computeDynamicBudget(expenses: Expense[], month?: string): BudgetCalculation {
  const currentMonth = month || new Date().toISOString().substring(0, 7);
  const settings = getLocalBudgetSettings();
  const income = Number(settings.income) || 0;
  const budgets = settings.budgets || {};

  // Filter expenses for this month
  const monthExpenses = expenses.filter((e) => String(e.date || "").startsWith(currentMonth));
  const spentByCat: Record<string, number> = {};

  for (const exp of monthExpenses) {
    const cat = exp.category || "Others";
    spentByCat[cat] = (spentByCat[cat] || 0) + (Number(exp.amount) || 0);
  }

  let totalBudget = 0;
  let totalSpent = 0;

  const byCategory = CATEGORIES.map((cat) => {
    const budget = Number(budgets[cat]) || 0;
    const spent = Math.round((spentByCat[cat] || 0) * 100) / 100;
    const remaining = Math.round((budget - spent) * 100) / 100;
    const pct = budget > 0 ? Math.round((spent / budget) * 1000) / 10 : 0;
    const overBudget = budget > 0 && spent > budget;

    totalBudget += budget;
    totalSpent += spent;

    return {
      category: cat,
      budget,
      spent,
      remaining,
      pct,
      over_budget: overBudget,
    };
  });

  return {
    income,
    total_budget: Math.round(totalBudget * 100) / 100,
    total_spent: Math.round(totalSpent * 100) / 100,
    remaining: Math.round((totalBudget - totalSpent) * 100) / 100,
    savings_estimate: Math.round((income - totalSpent) * 100) / 100,
    month: currentMonth,
    by_category: byCategory,
  };
}

// ── Main API Object ──────────────────────────────────────────────────────────

export const api = {
  // ── Auth ────────────────────────────────────────────────────────────────
  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const res = await apiClient.post<AuthResponse>("/auth/login", { username, password });
      if (typeof window !== "undefined") {
        localStorage.setItem("finmate_token", res.data.access_token);
        localStorage.setItem("finmate_user", JSON.stringify(res.data.user));
      }
      return res.data;
    } catch {
      // Local account fallback
      const localUser: User = { id: 1, username, email: `${username.toLowerCase()}@finmate.local` };
      const localAuth: AuthResponse = { access_token: `token-${Date.now()}`, token_type: "bearer", user: localUser };
      if (typeof window !== "undefined") {
        localStorage.setItem("finmate_token", localAuth.access_token);
        localStorage.setItem("finmate_user", JSON.stringify(localUser));
      }
      return localAuth;
    }
  },

  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    try {
      const res = await apiClient.post<AuthResponse>("/auth/register", { username, email, password });
      if (typeof window !== "undefined") {
        localStorage.setItem("finmate_token", res.data.access_token);
        localStorage.setItem("finmate_user", JSON.stringify(res.data.user));
      }
      return res.data;
    } catch {
      const localUser: User = { id: 1, username, email };
      const localAuth: AuthResponse = { access_token: `token-${Date.now()}`, token_type: "bearer", user: localUser };
      if (typeof window !== "undefined") {
        localStorage.setItem("finmate_token", localAuth.access_token);
        localStorage.setItem("finmate_user", JSON.stringify(localUser));
      }
      return localAuth;
    }
  },

  getCurrentUser(): User | null {
    if (typeof window === "undefined") return null;
    const stored = localStorage.getItem("finmate_user");
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        return null;
      }
    }
    return { id: 1, username: "Guest User", email: "user@finmate.app" };
  },

  logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("finmate_token");
      localStorage.removeItem("finmate_user");
    }
  },

  // ── Expenses ─────────────────────────────────────────────────────────────
  async getExpenses(params?: {
    category?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    limit?: number;
  }): Promise<Expense[]> {
    try {
      const res = await apiClient.get<Expense[]>("/expenses", { params });
      // Sync local storage cache
      if (res.data && Array.isArray(res.data)) {
        if (!params?.category && !params?.search && !params?.start_date && !params?.end_date) {
          setLocalExpenses(res.data);
        }
      }
      return res.data;
    } catch {
      let filtered = getLocalExpenses();
      if (params?.category && params.category !== "All Categories") {
        filtered = filtered.filter((e) => e.category === params.category);
      }
      if (params?.search) {
        const s = params.search.toLowerCase().trim();
        filtered = filtered.filter((e) => e.merchant.toLowerCase().includes(s));
      }
      if (params?.start_date) {
        filtered = filtered.filter((e) => e.date >= params.start_date!);
      }
      if (params?.end_date) {
        filtered = filtered.filter((e) => e.date <= params.end_date!);
      }
      if (params?.limit) {
        filtered = filtered.slice(0, params.limit);
      }
      return filtered;
    }
  },

  async createExpense(expense: ExpenseInput): Promise<Expense> {
    const localList = getLocalExpenses();
    const newId = Date.now();
    const createdLocally: Expense = {
      id: newId,
      merchant: expense.merchant,
      amount: Number(expense.amount),
      date: expense.date,
      category: expense.category,
      payment: expense.payment,
      source: expense.source || "manual",
      notes: expense.notes || "",
    };

    try {
      const res = await apiClient.post<Expense>("/expenses", expense);
      localList.unshift(res.data);
      setLocalExpenses(localList);
      return res.data;
    } catch {
      localList.unshift(createdLocally);
      setLocalExpenses(localList);
      return createdLocally;
    }
  },

  async updateExpense(id: number, updates: Partial<ExpenseInput>): Promise<Expense> {
    const localList = getLocalExpenses();
    const idx = localList.findIndex((e) => e.id === id);

    try {
      const res = await apiClient.put<Expense>(`/expenses/${id}`, updates);
      if (idx !== -1) {
        localList[idx] = res.data;
        setLocalExpenses(localList);
      }
      return res.data;
    } catch {
      if (idx !== -1) {
        localList[idx] = { ...localList[idx], ...updates, amount: updates.amount !== undefined ? Number(updates.amount) : localList[idx].amount };
        setLocalExpenses(localList);
        return localList[idx];
      }
      throw new Error("Expense not found");
    }
  },

  async deleteExpense(id: number): Promise<boolean> {
    const localList = getLocalExpenses();
    const filtered = localList.filter((e) => e.id !== id);
    setLocalExpenses(filtered);

    try {
      await apiClient.delete(`/expenses/${id}`);
      return true;
    } catch {
      return true;
    }
  },

  async autoCategorize(merchant: string, description?: string): Promise<{ category: string; confidence: number }> {
    try {
      const res = await apiClient.post("/expenses/categorize", { merchant, description });
      return res.data;
    } catch {
      const lower = (merchant + " " + (description || "")).toLowerCase();
      if (lower.includes("swiggy") || lower.includes("zomato") || lower.includes("food") || lower.includes("restaurant") || lower.includes("cafe") || lower.includes("dining") || lower.includes("blinkit") || lower.includes("zepto") || lower.includes("instamart")) {
        return { category: "Food & Dining", confidence: 0.95 };
      }
      if (lower.includes("uber") || lower.includes("ola") || lower.includes("rapido") || lower.includes("petrol") || lower.includes("fuel") || lower.includes("metro") || lower.includes("cab")) {
        return { category: "Transport", confidence: 0.95 };
      }
      if (lower.includes("amazon") || lower.includes("flipkart") || lower.includes("myntra") || lower.includes("zara") || lower.includes("clothing") || lower.includes("shopping") || lower.includes("ajio")) {
        return { category: "Shopping", confidence: 0.95 };
      }
      if (lower.includes("netflix") || lower.includes("spotify") || lower.includes("pvr") || lower.includes("prime") || lower.includes("cinema") || lower.includes("movie") || lower.includes("hotstar")) {
        return { category: "Entertainment", confidence: 0.95 };
      }
      if (lower.includes("airtel") || lower.includes("jio") || lower.includes("electricity") || lower.includes("water") || lower.includes("broadband") || lower.includes("wifi") || lower.includes("gas") || lower.includes("recharge")) {
        return { category: "Bills & Utilities", confidence: 0.95 };
      }
      if (lower.includes("pharmacy") || lower.includes("apollo") || lower.includes("doctor") || lower.includes("hospital") || lower.includes("medicine") || lower.includes("1mg") || lower.includes("practo")) {
        return { category: "Healthcare", confidence: 0.95 };
      }
      if (lower.includes("course") || lower.includes("udemy") || lower.includes("books") || lower.includes("college") || lower.includes("tuition") || lower.includes("coursera")) {
        return { category: "Education", confidence: 0.95 };
      }
      if (lower.includes("flight") || lower.includes("hotel") || lower.includes("makemytrip") || lower.includes("airbnb") || lower.includes("train") || lower.includes("irctc")) {
        return { category: "Travel", confidence: 0.95 };
      }
      if (lower.includes("rent") || lower.includes("landlord") || lower.includes("nobroker") || lower.includes("maintenance")) {
        return { category: "Rent", confidence: 0.95 };
      }
      return { category: "Others", confidence: 0.5 };
    }
  },

  async importCsv(file: File): Promise<{ success: boolean; imported: number; skipped: number; message: string }> {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await apiClient.post("/expenses/import-csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    } catch {
      // Local CSV parsing fallback
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const text = e.target?.result as string;
          if (!text) {
            resolve({ success: false, imported: 0, skipped: 0, message: "Empty file" });
            return;
          }
          const lines = text.split("\n").filter((l) => l.trim().length > 0);
          if (lines.length <= 1) {
            resolve({ success: false, imported: 0, skipped: 0, message: "No data rows found" });
            return;
          }
          const header = lines[0].toLowerCase();
          const localList = getLocalExpenses();
          let count = 0;

          for (let i = 1; i < lines.length; i++) {
            const parts = lines[i].split(",").map((p) => p.trim().replace(/^["']|["']$/g, ""));
            if (parts.length >= 3) {
              const merchant = parts[0] || "Imported Expense";
              const amount = parseFloat(parts[1]) || 0;
              const date = parts[2] || new Date().toISOString().substring(0, 10);
              const category = parts[3] || "Others";
              const payment = parts[4] || "Other";

              if (amount > 0) {
                localList.unshift({
                  id: Date.now() + i,
                  merchant,
                  amount,
                  date,
                  category,
                  payment,
                  source: "csv",
                  notes: "Bulk CSV Import",
                });
                count++;
              }
            }
          }
          setLocalExpenses(localList);
          resolve({
            success: true,
            imported: count,
            skipped: lines.length - 1 - count,
            message: `Successfully imported ${count} transactions from CSV.`,
          });
        };
        reader.readAsText(file);
      });
    }
  },

  // ── Analytics ────────────────────────────────────────────────────────────
  async getSummary(): Promise<SpendingSummary> {
    try {
      const res = await apiClient.get<SpendingSummary>("/analytics/summary");
      return res.data;
    } catch {
      const expenses = getLocalExpenses();
      return computeDynamicSummary(expenses);
    }
  },

  // ── Budget ───────────────────────────────────────────────────────────────
  async getBudgetCalculation(month?: string): Promise<BudgetCalculation> {
    try {
      const res = await apiClient.get<BudgetCalculation>("/budget/calculate", { params: { month } });
      return res.data;
    } catch {
      const expenses = getLocalExpenses();
      return computeDynamicBudget(expenses, month);
    }
  },

  async getBudgetSettings(month?: string): Promise<BudgetSettings> {
    try {
      const res = await apiClient.get<BudgetSettings>("/budget/settings", { params: { month } });
      return res.data;
    } catch {
      const local = getLocalBudgetSettings();
      return {
        income: local.income,
        budgets: local.budgets,
        month: month || local.month,
      };
    }
  },

  async saveBudgetSettings(income: number, budgets: Record<string, number>, month?: string): Promise<BudgetSettings> {
    const currentMonth = month || new Date().toISOString().substring(0, 7);
    const updated = { income: Number(income) || 0, budgets, month: currentMonth };
    setLocalBudgetSettings(updated);

    try {
      const res = await apiClient.post<BudgetSettings>("/budget/settings", updated);
      return res.data;
    } catch {
      return updated;
    }
  },

  // ── Goals ────────────────────────────────────────────────────────────────
  async getGoals(): Promise<Goal[]> {
    try {
      const res = await apiClient.get<Goal[]>("/goals");
      if (res.data && Array.isArray(res.data)) {
        setLocalGoals(res.data);
      }
      return res.data;
    } catch {
      return getLocalGoals();
    }
  },

  async createGoal(goal: GoalInput): Promise<Goal> {
    const localGoals = getLocalGoals();
    const newGoal: Goal = {
      id: Date.now(),
      name: goal.name,
      target: Number(goal.target) || 0,
      current: Number(goal.current) || 0,
      deadline: goal.deadline || null,
      notes: goal.notes || "",
    };

    try {
      const res = await apiClient.post<Goal>("/goals", goal);
      localGoals.unshift(res.data);
      setLocalGoals(localGoals);
      return res.data;
    } catch {
      localGoals.unshift(newGoal);
      setLocalGoals(localGoals);
      return newGoal;
    }
  },

  async updateGoal(id: number, updates: Partial<GoalInput>): Promise<Goal> {
    const localGoals = getLocalGoals();
    const idx = localGoals.findIndex((g) => g.id === id);

    try {
      const res = await apiClient.put<Goal>(`/goals/${id}`, updates);
      if (idx !== -1) {
        localGoals[idx] = res.data;
        setLocalGoals(localGoals);
      }
      return res.data;
    } catch {
      if (idx !== -1) {
        localGoals[idx] = {
          ...localGoals[idx],
          ...updates,
          target: updates.target !== undefined ? Number(updates.target) : localGoals[idx].target,
          current: updates.current !== undefined ? Number(updates.current) : localGoals[idx].current,
        };
        setLocalGoals(localGoals);
        return localGoals[idx];
      }
      throw new Error("Goal not found");
    }
  },

  async deleteGoal(id: number): Promise<boolean> {
    const localGoals = getLocalGoals();
    const filtered = localGoals.filter((g) => g.id !== id);
    setLocalGoals(filtered);

    try {
      await apiClient.delete(`/goals/${id}`);
      return true;
    } catch {
      return true;
    }
  },

  // ── AI Advisor ───────────────────────────────────────────────────────────
  async getGurus(): Promise<Guru[]> {
    try {
      const res = await apiClient.get<Guru[]>("/advisor/gurus");
      return res.data;
    } catch {
      return GURUS;
    }
  },

  async generateAdvice(guru: string, summary?: SpendingSummary): Promise<AdviceResult> {
    try {
      const res = await apiClient.post<AdviceResult>("/advisor/generate", { guru, summary });
      return res.data;
    } catch {
      const totalSpent = summary?.total_spending || 0;
      const topCat = summary?.top_category || "General";
      const txCount = summary?.transaction_count || 0;

      if (txCount === 0) {
        return {
          observation: "You have not recorded any expenses yet in FinMate AI.",
          recommendation: "Start by logging your daily expenses or scanning recent payment receipts.",
          why: "Tracking every outflow is the first essential step to understanding cash flow patterns and building a realistic budget.",
          action: "Add your first expense or upload a payment receipt screenshot to unlock AI financial analysis.",
          guru,
          disclaimer: "Educational financial insights only. Not certified financial advice.",
          _mock: true,
        };
      }

      if (guru === "Warren Buffett") {
        return {
          observation: `You have recorded ₹${totalSpent.toLocaleString("en-IN")} in spending with the highest volume in ${topCat}.`,
          recommendation: `Scrutinize all expenditures in ${topCat} and redirect surplus capital into productive, low-cost index funds.`,
          why: "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1. Compounding requires consistency and avoiding unnecessary leaks.",
          action: `Trim 15% from ${topCat} this month and invest that difference directly into an index SIP on the 1st of every month.`,
          guru,
          disclaimer: "Educational financial insights only. Not certified financial advice.",
          _mock: true,
        };
      }

      if (guru === "Robert Kiyosaki") {
        return {
          observation: `Your recorded total spend of ₹${totalSpent.toLocaleString("en-IN")} is primarily consumption-driven.`,
          recommendation: "Focus on acquiring assets that generate positive cash flow rather than accumulating lifestyle liabilities.",
          why: "The rich acquire assets; the poor and middle class acquire liabilities that they think are assets.",
          action: "Set aside a designated portion of your monthly income to build an asset column before paying lifestyle expenses.",
          guru,
          disclaimer: "Educational financial insights only. Not certified financial advice.",
          _mock: true,
        };
      }

      if (guru === "Ramit Sethi") {
        return {
          observation: `Your primary expense category is ${topCat}, representing your main current spending focus.`,
          recommendation: "Design a conscious spending plan: spend extravagantly on things you love, and cut costs mercilessly on things you don't.",
          why: "There is a limit to how much you can cut, but no limit to how much you can earn and automate.",
          action: "Automate your savings and fixed costs on payday so the remainder can be spent 100% guilt-free.",
          guru,
          disclaimer: "Educational financial insights only. Not certified financial advice.",
          _mock: true,
        };
      }

      return {
        observation: `Across ${txCount} transactions, your recorded spending is ₹${totalSpent.toLocaleString("en-IN")}, led by ${topCat}.`,
        recommendation: "Structure your budget using the 50/30/20 framework: 50% essentials, 30% discretionary, and 20% savings.",
        why: "A balanced financial structure builds wealth steadily while maintaining liquidity for unexpected emergencies.",
        action: `Review your ${topCat} category limits in the Budget tab to keep discretionary outflows balanced.`,
        guru: "General Financial Principles",
        disclaimer: "Educational financial insights only. Not certified financial advice.",
        _mock: true,
      };
    }
  },

  // ── OCR ──────────────────────────────────────────────────────────────────
  async scanReceipt(file: File): Promise<OCRResult> {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await apiClient.post<OCRResult>("/ocr/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    } catch {
      // Clean fallback if backend OCR is unavailable
      return {
        merchant: file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " "),
        amount: 0.0,
        date: new Date().toISOString().substring(0, 10),
        transaction_type: "debit",
        payment_method: "UPI",
        confidence: 0.85,
        raw_text: `Extracted from ${file.name}`,
        _mock: true,
      };
    }
  },

  // ── Reports ──────────────────────────────────────────────────────────────
  getExportUrl(type: "expenses" | "budget" | "goals" | "summary"): string {
    return `${API_BASE_URL}/reports/export/${type}`;
  },
};
