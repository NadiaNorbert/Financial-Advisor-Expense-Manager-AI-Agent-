"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Search,
  Filter,
  Plus,
  Edit2,
  Trash2,
  Download,
  LayoutGrid,
  List as ListIcon,
  Receipt,
  Calendar,
  CreditCard,
  Tag,
  AlertCircle,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import {
  formatINR,
  formatDate,
  CATEGORIES,
  PAYMENT_METHODS,
  CATEGORY_COLORS,
} from "@/lib/utils";
import { Expense, ExpenseInput } from "@/types";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [sortBy, setSortBy] = useState<"date_desc" | "date_asc" | "amt_desc" | "amt_asc" | "merchant">("date_desc");

  // Filters
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All Categories");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Add/Edit Form State
  const [formData, setFormData] = useState<ExpenseInput>({
    merchant: "",
    amount: 0,
    date: new Date().toISOString().split("T")[0],
    category: "Food & Dining",
    payment: "UPI",
    notes: "",
  });
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [autoCatSuggestion, setAutoCatSuggestion] = useState<string | null>(null);

  useEffect(() => {
    loadExpenses();
  }, []);

  async function loadExpenses() {
    setLoading(true);
    try {
      const data = await api.getExpenses();
      setExpenses(data);
    } catch (err) {
      console.error("Failed to load expenses", err);
    } finally {
      setLoading(false);
    }
  }

  // Handle merchant input auto-categorize debounce
  const handleMerchantChange = async (val: string) => {
    setFormData((prev) => ({ ...prev, merchant: val }));
    if (val.trim().length >= 3) {
      const res = await api.autoCategorize(val);
      if (res.confidence > 0.6) {
        setAutoCatSuggestion(res.category);
      }
    } else {
      setAutoCatSuggestion(null);
    }
  };

  const handleOpenAdd = () => {
    setFormData({
      merchant: "",
      amount: 0,
      date: new Date().toISOString().split("T")[0],
      category: "Food & Dining",
      payment: "UPI",
      notes: "",
    });
    setAutoCatSuggestion(null);
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (exp: Expense) => {
    setEditingExpense(exp);
    setFormData({
      merchant: exp.merchant,
      amount: exp.amount,
      date: exp.date,
      category: exp.category,
      payment: exp.payment,
      notes: exp.notes || "",
    });
    setAutoCatSuggestion(null);
  };

  const handleSaveExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.merchant.trim() || formData.amount <= 0) return;

    setFormSubmitting(true);
    try {
      if (editingExpense) {
        const updated = await api.updateExpense(editingExpense.id, formData);
        setExpenses((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        setEditingExpense(null);
      } else {
        const created = await api.createExpense(formData);
        setExpenses((prev) => [created, ...prev]);
        setIsAddModalOpen(false);
      }
    } catch (err) {
      console.error("Failed to save expense", err);
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDeleteExpense = async (id: number) => {
    try {
      await api.deleteExpense(id);
      setExpenses((prev) => prev.filter((item) => item.id !== id));
      setDeletingId(null);
    } catch (err) {
      console.error("Failed to delete expense", err);
    }
  };

  // Filter and Sort Pipeline
  const filteredExpenses = useMemo(() => {
    let list = [...expenses];

    if (search.trim()) {
      const s = search.toLowerCase();
      list = list.filter((e) => e.merchant.toLowerCase().includes(s));
    }

    if (categoryFilter !== "All Categories") {
      list = list.filter((e) => e.category === categoryFilter);
    }

    if (startDate) {
      list = list.filter((e) => e.date >= startDate);
    }

    if (endDate) {
      list = list.filter((e) => e.date <= endDate);
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === "date_desc") return b.date.localeCompare(a.date);
      if (sortBy === "date_asc") return a.date.localeCompare(b.date);
      if (sortBy === "amt_desc") return b.amount - a.amount;
      if (sortBy === "amt_asc") return a.amount - b.amount;
      if (sortBy === "merchant") return a.merchant.localeCompare(b.merchant);
      return 0;
    });

    return list;
  }, [expenses, search, categoryFilter, startDate, endDate, sortBy]);

  const totalFilteredAmount = filteredExpenses.reduce((sum, e) => sum + e.amount, 0);

  const handleExportCSV = () => {
    const csvContent =
      "data:text/csv;charset=utf-8," +
      ["Date,Merchant,Category,Amount,Payment,Notes"]
        .concat(
          filteredExpenses.map(
            (e) =>
              `"${e.date}","${e.merchant.replace(/"/g, '""')}","${e.category}",${e.amount},"${e.payment}","${(e.notes || "").replace(/"/g, '""')}"`
          )
        )
        .join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `finmate_expenses_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
            Expense Management
          </h1>
          <p className="text-sm text-slate-400">
            Search, filter, categorize, and organize your transaction history.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExportCSV}>
            <Download className="h-4 w-4" />
            <span className="hidden sm:inline">Export CSV</span>
          </Button>
          <Button variant="primary" size="sm" onClick={handleOpenAdd}>
            <Plus className="h-4 w-4" />
            <span>Add Expense</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4 sm:p-5 border-slate-800 space-y-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <Input
              placeholder="Search merchant..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Category */}
          <Select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="All Categories">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </Select>

          {/* Date From */}
          <Input
            type="date"
            placeholder="From"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />

          {/* Date To */}
          <Input
            type="date"
            placeholder="To"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        {/* Filter Summary & View Mode Toggles */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 pt-3 text-xs">
          <div className="flex items-center gap-4 text-slate-400">
            <span>
              Showing <strong className="text-slate-200">{filteredExpenses.length}</strong> of {expenses.length}
            </span>
            <span>•</span>
            <span>
              Total: <strong className="text-teal-400 font-semibold">{formatINR(totalFilteredAmount, 2)}</strong>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <span className="text-slate-400 hidden sm:inline">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="rounded-lg border border-slate-800 bg-slate-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
              >
                <option value="date_desc">Date (Newest)</option>
                <option value="date_asc">Date (Oldest)</option>
                <option value="amt_desc">Amount (High to Low)</option>
                <option value="amt_asc">Amount (Low to High)</option>
                <option value="merchant">Merchant (A-Z)</option>
              </select>
            </div>

            <div className="flex items-center rounded-lg border border-slate-800 bg-slate-950 p-0.5">
              <button
                onClick={() => setViewMode("cards")}
                className={`rounded-md p-1.5 transition-colors ${
                  viewMode === "cards" ? "bg-slate-800 text-teal-400" : "text-slate-500 hover:text-slate-300"
                }`}
                title="Card View"
              >
                <LayoutGrid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`rounded-md p-1.5 transition-colors ${
                  viewMode === "table" ? "bg-slate-800 text-teal-400" : "text-slate-500 hover:text-slate-300"
                }`}
                title="Table View"
              >
                <ListIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Expenses Display */}
      {filteredExpenses.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center">
          <div className="rounded-full bg-slate-800 p-4 text-slate-500 mb-3">
            <Receipt className="h-8 w-8" />
          </div>
          <h3 className="text-base font-semibold text-slate-200">No expenses found</h3>
          <p className="mt-1 text-xs text-slate-400 max-w-sm">
            Try clearing or adjusting your search filters, or add a new transaction.
          </p>
          <Button variant="primary" size="sm" onClick={handleOpenAdd} className="mt-4">
            <Plus className="h-4 w-4" /> Add Expense
          </Button>
        </Card>
      ) : viewMode === "cards" ? (
        /* Cards View */
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredExpenses.map((expense) => {
            const catColor = CATEGORY_COLORS[expense.category] || "#64748B";
            return (
              <Card
                key={expense.id}
                className="p-4 hover:border-slate-700 transition-all group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <div
                        className="flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold text-white shadow-sm"
                        style={{ backgroundColor: `${catColor}33`, borderColor: `${catColor}66`, borderWidth: "1px" }}
                      >
                        {expense.merchant.charAt(0)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-100 text-sm">{expense.merchant}</h4>
                        <span className="text-[11px] text-slate-400">{formatDate(expense.date)}</span>
                      </div>
                    </div>
                    <span className="text-base font-bold text-slate-100">{formatINR(expense.amount, 2)}</span>
                  </div>

                  <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <Badge variant="teal" className="text-[10px]">
                      <Tag className="h-3 w-3" /> {expense.category}
                    </Badge>
                    <Badge variant="slate" className="text-[10px]">
                      <CreditCard className="h-3 w-3" /> {expense.payment}
                    </Badge>
                  </div>

                  {expense.notes && (
                    <p className="mt-2.5 text-xs text-slate-400 bg-slate-950/40 p-2 rounded-lg border border-slate-800/60 line-clamp-2">
                      {expense.notes}
                    </p>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-end gap-2 border-t border-slate-800/60 pt-2.5">
                  <button
                    onClick={() => handleOpenEdit(expense)}
                    className="p-1 text-slate-400 hover:text-teal-400 transition-colors"
                    title="Edit"
                  >
                    <Edit2 className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => setDeletingId(expense.id)}
                    className="p-1 text-slate-400 hover:text-rose-400 transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        /* Table View */
        <Card className="overflow-hidden p-0 border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 bg-slate-950 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Merchant</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Payment</th>
                  <th className="px-4 py-3 text-right">Amount</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredExpenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap text-slate-400">{formatDate(expense.date)}</td>
                    <td className="px-4 py-3 font-semibold text-slate-200">
                      {expense.merchant}
                      {expense.notes && <span className="block text-[10px] text-slate-500">{expense.notes}</span>}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="teal" className="text-[10px]">
                        {expense.category}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{expense.payment}</td>
                    <td className="px-4 py-3 text-right font-bold text-slate-100 whitespace-nowrap">
                      {formatINR(expense.amount, 2)}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenEdit(expense)}
                          className="p-1 text-slate-400 hover:text-teal-400"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => setDeletingId(expense.id)}
                          className="p-1 text-slate-400 hover:text-rose-400"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Add / Edit Modal */}
      <Modal
        isOpen={isAddModalOpen || editingExpense !== null}
        onClose={() => {
          setIsAddModalOpen(false);
          setEditingExpense(null);
        }}
        title={editingExpense ? "Edit Expense" : "Add New Expense"}
        description={
          editingExpense
            ? `Update details for transaction #${editingExpense.id}`
            : "Record a manual transaction into your expense database."
        }
      >
        <form onSubmit={handleSaveExpense} className="space-y-4">
          <Input
            label="Merchant / Payee *"
            placeholder="e.g. Swiggy, Uber, Amazon"
            value={formData.merchant}
            onChange={(e) => handleMerchantChange(e.target.value)}
            required
          />

          {autoCatSuggestion && (
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-teal-500/10 border border-teal-500/20 text-xs">
              <div className="flex items-center gap-1.5 text-teal-300">
                <Tag className="h-3.5 w-3.5" />
                <span>Suggested category: <strong>{autoCatSuggestion}</strong></span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setFormData((prev) => ({ ...prev, category: autoCatSuggestion }));
                  setAutoCatSuggestion(null);
                }}
                className="text-[11px] font-bold text-teal-400 underline hover:text-teal-300"
              >
                Apply
              </button>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Amount (₹) *"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="450.00"
              value={formData.amount || ""}
              onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
              required
            />
            <Input
              label="Date *"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Category *"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </Select>

            <Select
              label="Payment Method *"
              value={formData.payment}
              onChange={(e) => setFormData({ ...formData, payment: e.target.value })}
            >
              {PAYMENT_METHODS.map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </Select>
          </div>

          <Input
            label="Notes (optional)"
            placeholder="e.g. Lunch with team, monthly billing"
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
                setEditingExpense(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={formSubmitting}>
              {editingExpense ? "Save Changes" : "Create Expense"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deletingId !== null}
        onClose={() => setDeletingId(null)}
        title="Delete Expense"
        description="Are you sure you want to delete this expense? This action cannot be undone."
      >
        <div className="flex justify-end gap-2 pt-3">
          <Button variant="outline" size="sm" onClick={() => setDeletingId(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => deletingId !== null && handleDeleteExpense(deletingId)}
          >
            Confirm Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}
