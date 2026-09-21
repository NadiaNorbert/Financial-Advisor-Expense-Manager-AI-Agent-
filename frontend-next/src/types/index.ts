/**
 * FinMate AI - TypeScript Type Definitions
 */

export interface User {
  id: number;
  username: string;
  email: string;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Expense {
  id: number;
  merchant: string;
  amount: number;
  date: string; // YYYY-MM-DD
  category: string;
  payment: string;
  source?: string;
  notes?: string | null;
  user_id?: number | null;
  created_at?: string | null;
}

export interface ExpenseInput {
  merchant: string;
  amount: number;
  date: string;
  category: string;
  payment: string;
  notes?: string | null;
  source?: string;
}

export interface CategoryBudget {
  category: string;
  budget: number;
  spent: number;
  remaining: number;
  pct: number;
  over_budget: boolean;
}

export interface BudgetCalculation {
  income: number;
  total_budget: number;
  total_spent: number;
  remaining: number;
  savings_estimate: number;
  by_category: CategoryBudget[];
  month: string;
}

export interface BudgetSettings {
  income: number;
  budgets: Record<string, number>;
  month: string;
}

export interface Goal {
  id: number;
  name: string;
  target: number;
  current: number;
  deadline?: string | null;
  notes?: string | null;
  user_id?: number | null;
  created_at?: string | null;
}

export interface GoalInput {
  name: string;
  target: number;
  current: number;
  deadline?: string | null;
  notes?: string | null;
}

export interface SpendingSummary {
  total_spending: number;
  monthly_spending: number;
  by_category: Record<string, number>;
  monthly_trend: Array<{ month: string; amount: number }>;
  daily_spending: Array<{ date: string; amount: number }>;
  top_category: string;
  transaction_count: number;
}

export interface Guru {
  id: string;
  name: string;
  emoji: string;
  tagline: string;
  color: string;
}

export interface AdviceResult {
  observation: string;
  recommendation: string;
  why: string;
  action: string;
  guru: string;
  disclaimer: string;
  _mock?: boolean;
}

export interface OCRResult {
  merchant?: string | null;
  amount?: number | null;
  date?: string | null;
  transaction_type?: string | null;
  payment_method?: string | null;
  confidence: number;
  raw_text?: string;
  error?: string | null;
  _mock?: boolean;
}

export interface SplitMember {
  name: string;
  share: number;
}

export interface SplitHistoryItem {
  id?: number | string;
  description: string;
  total: number;
  your_share: number;
  members: number;
  paid_by?: string;
  date: string;
  category: string;
}
