"use client";

import React, { useState } from "react";
import {
  Users2,
  Receipt,
  Plus,
  ArrowRight,
  CheckCircle2,
  Calendar,
  CreditCard,
  Tag,
  Divide,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { formatINR, CATEGORIES, PAYMENT_METHODS } from "@/lib/utils";
import { SplitHistoryItem } from "@/types";

export default function SplitPage() {
  const [activeTab, setActiveTab] = useState<"split" | "history">("split");

  // Form State
  const [description, setDescription] = useState("");
  const [totalAmount, setTotalAmount] = useState<number>(0);
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [category, setCategory] = useState("Food & Dining");
  const [payment, setPayment] = useState("UPI");
  const [paidBy, setPaidBy] = useState("You");
  const [numMembers, setNumMembers] = useState(3);
  const [splitMode, setSplitMode] = useState<"equal" | "custom">("equal");

  // Member names
  const [memberNames, setMemberNames] = useState<string[]>(["You", "Rahul", "Pooja"]);
  const [customShares, setCustomShares] = useState<number[]>([0, 0, 0]);

  // Status & History
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [splitHistory, setSplitHistory] = useState<SplitHistoryItem[]>([]);

  React.useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem("finmate_split_history");
        if (stored) {
          setSplitHistory(JSON.parse(stored));
        }
      } catch {}
    }
  }, []);

  const handleNumMembersChange = (num: number) => {
    const val = Math.max(2, Math.min(20, num));
    setNumMembers(val);
    const newNames = Array.from({ length: val }, (_, i) => memberNames[i] || (i === 0 ? "You" : `Person ${i + 1}`));
    setMemberNames(newNames);
    const newShares = Array.from({ length: val }, (_, i) => customShares[i] || 0);
    setCustomShares(newShares);
  };

  const yourShare = splitMode === "equal"
    ? numMembers > 0 ? Math.round((totalAmount / numMembers) * 100) / 100 : 0
    : customShares[0] || 0;

  const handleImportMyShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || totalAmount <= 0 || yourShare <= 0) return;

    setSaving(true);
    try {
      const otherMembers = memberNames.slice(1).filter(Boolean).join(", ");
      const autoNotes = `Split ${numMembers} ways with ${otherMembers} (Paid by: ${paidBy})`;

      await api.createExpense({
        merchant: description.trim(),
        amount: yourShare,
        date,
        category,
        payment,
        notes: autoNotes,
        source: "split",
      });

      const newHistoryItem: SplitHistoryItem = {
        id: Date.now(),
        description: description.trim(),
        total: totalAmount,
        your_share: yourShare,
        members: numMembers,
        paid_by: paidBy,
        date,
        category,
      };

      setSplitHistory((prev) => {
        const updated = [newHistoryItem, ...prev];
        if (typeof window !== "undefined") {
          localStorage.setItem("finmate_split_history", JSON.stringify(updated));
        }
        return updated;
      });
      setSuccessMsg(`Your share of ${formatINR(yourShare, 2)} for "${description}" has been added to expenses!`);

      // Reset form
      setDescription("");
      setTotalAmount(0);
      setTimeout(() => setSuccessMsg(null), 5000);
    } catch (err) {
      console.error("Failed to import split expense", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Split Shared Expenses
        </h1>
        <p className="text-sm text-slate-400">
          Split group bills, calculate fair shares, and import your portion directly into your expense tracker.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab("split")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "split"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Divide className="h-4 w-4" />
          <span>Split Calculator</span>
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "history"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Users2 className="h-4 w-4" />
          <span>Split History</span>
        </button>
      </div>

      {/* ── TAB 1: Split Calculator ─────────────────────────────────── */}
      {activeTab === "split" && (
        <Card className="max-w-3xl mx-auto p-6 border-slate-800">
          <CardHeader className="mb-4">
            <div>
              <CardTitle>Calculate & Split Shared Bill</CardTitle>
              <p className="text-xs text-slate-400">
                Enter total bill and participants to compute your share
              </p>
            </div>
          </CardHeader>

          {successMsg && (
            <div className="mb-4 flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3.5 text-xs text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleImportMyShare} className="space-y-4">
            <Input
              label="Expense Description *"
              placeholder="e.g. Dinner at Barbeque Nation, Goa Villa Booking"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Total Bill Amount (₹) *"
                type="number"
                min="0.01"
                step="0.01"
                placeholder="3600.00"
                value={totalAmount || ""}
                onChange={(e) => setTotalAmount(parseFloat(e.target.value) || 0)}
                required
              />
              <Input
                label="Date *"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <Select
                label="Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </Select>

              <Select
                label="Payment Method"
                value={payment}
                onChange={(e) => setPayment(e.target.value)}
              >
                {PAYMENT_METHODS.map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </Select>

              <Input
                label="Paid By"
                placeholder="e.g. You / Rahul"
                value={paidBy}
                onChange={(e) => setPaidBy(e.target.value)}
              />
            </div>

            {/* Split Mode & Participants */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-medium text-slate-300">Number of people:</span>
                  <input
                    type="number"
                    min="2"
                    max="20"
                    value={numMembers}
                    onChange={(e) => handleNumMembersChange(parseInt(e.target.value) || 2)}
                    className="w-16 rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-center text-sm font-semibold text-slate-100"
                  />
                </div>

                <div className="flex rounded-lg border border-slate-800 bg-slate-900 p-0.5 text-xs">
                  <button
                    type="button"
                    onClick={() => setSplitMode("equal")}
                    className={`rounded px-3 py-1 font-medium transition-colors ${
                      splitMode === "equal" ? "bg-teal-500 text-slate-950 font-bold" : "text-slate-400"
                    }`}
                  >
                    Equal Split
                  </button>
                  <button
                    type="button"
                    onClick={() => setSplitMode("custom")}
                    className={`rounded px-3 py-1 font-medium transition-colors ${
                      splitMode === "custom" ? "bg-teal-500 text-slate-950 font-bold" : "text-slate-400"
                    }`}
                  >
                    Custom Shares
                  </button>
                </div>
              </div>

              {/* Your Share Highlight Banner */}
              <div className="rounded-xl bg-gradient-to-r from-teal-500/10 to-emerald-500/10 border border-teal-500/30 p-4 text-center">
                <span className="text-xs text-slate-400">Your Share ({numMembers} participants)</span>
                <div className="mt-1 text-3xl font-extrabold text-teal-300">
                  {formatINR(yourShare, 2)}
                </div>
                <p className="mt-1 text-[11px] text-slate-400">
                  = {formatINR(totalAmount, 2)} ÷ {numMembers} members
                </p>
              </div>

              {/* Member Names Inputs */}
              <div>
                <span className="text-xs font-medium text-slate-400 block mb-2">Participant Names:</span>
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                  {Array.from({ length: numMembers }).map((_, idx) => (
                    <input
                      key={idx}
                      type="text"
                      placeholder={idx === 0 ? "You" : `Person ${idx + 1}`}
                      value={memberNames[idx] || ""}
                      onChange={(e) => {
                        const newNames = [...memberNames];
                        newNames[idx] = e.target.value;
                        setMemberNames(newNames);
                      }}
                      className="rounded-lg border border-slate-800 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-200"
                    />
                  ))}
                </div>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={saving}
            >
              <Plus className="h-4 w-4" /> Import My Share to Expenses ({formatINR(yourShare, 2)})
            </Button>
          </form>
        </Card>
      )}

      {/* ── TAB 2: Split History ────────────────────────────────────── */}
      {activeTab === "history" && (
        <div className="space-y-4">
          {splitHistory.length === 0 ? (
            <Card className="p-10 text-center text-slate-500 border-slate-800">
              <Users2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No split history recorded yet.</p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {splitHistory.map((item, idx) => (
                <Card key={idx} className="p-4 border-slate-800 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between">
                      <h4 className="font-semibold text-sm text-slate-100">{item.description}</h4>
                      <Badge variant="teal">{item.category}</Badge>
                    </div>
                    <div className="mt-1 flex items-center gap-2 text-xs text-slate-400">
                      <span>{item.date}</span>
                      <span>•</span>
                      <span>{item.members} members</span>
                      <span>•</span>
                      <span>Paid by {item.paid_by || "You"}</span>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-2 text-xs">
                    <div>
                      <span className="text-slate-500">Total Bill:</span>{" "}
                      <strong className="text-slate-300">{formatINR(item.total, 2)}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500">Your Share:</span>{" "}
                      <strong className="text-teal-400 font-bold text-sm">
                        {formatINR(item.your_share, 2)}
                      </strong>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
