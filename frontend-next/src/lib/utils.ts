import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatINR(amount: number, decimals: number = 0): string {
  if (amount === undefined || amount === null || isNaN(amount)) return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function formatRelativeDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    const today = new Date();
    const diffTime = today.getTime() - d.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return formatDate(dateStr);
  } catch {
    return dateStr;
  }
}

export const CATEGORIES = [
  "Food & Dining",
  "Transport",
  "Shopping",
  "Entertainment",
  "Bills & Utilities",
  "Healthcare",
  "Education",
  "Travel",
  "Rent",
  "Others",
] as const;

export const PAYMENT_METHODS = [
  "UPI",
  "Debit Card",
  "Credit Card",
  "Net Banking",
  "Cash",
  "Wallet",
  "Other",
] as const;

export const CATEGORY_COLORS: Record<string, string> = {
  "Food & Dining": "#14B8A6", // Teal
  "Transport": "#3B82F6",    // Blue
  "Shopping": "#EC4899",     // Pink
  "Entertainment": "#8B5CF6",// Purple
  "Bills & Utilities": "#F59E0B", // Amber
  "Healthcare": "#EF4444",   // Red
  "Education": "#06B6D4",    // Cyan
  "Travel": "#10B981",       // Emerald
  "Rent": "#6366F1",         // Indigo
  "Others": "#64748B",       // Slate
};
