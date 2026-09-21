"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Lightbulb,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { formatINR } from "@/lib/utils";
import { GURUS } from "@/lib/mock-data";
import { SpendingSummary, BudgetCalculation, AdviceResult, Guru } from "@/types";

export default function AdvisorPage() {
  const [gurus, setGurus] = useState<Guru[]>(GURUS);
  const [selectedGuru, setSelectedGuru] = useState<string>("General Financial Principles");
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [budgetData, setBudgetData] = useState<BudgetCalculation | null>(null);
  const [advice, setAdvice] = useState<AdviceResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadAdvisorSnapshot() {
      try {
        const [sum, bud, guruList] = await Promise.all([
          api.getSummary(),
          api.getBudgetCalculation(),
          api.getGurus(),
        ]);
        setSummary(sum);
        setBudgetData(bud);
        if (guruList && guruList.length > 0) {
          setGurus(guruList);
        }
      } catch (err) {
        console.error("Failed to load spending snapshot", err);
      }
    }
    loadAdvisorSnapshot();
  }, []);

  const handleGenerateAdvice = async () => {
    setLoading(true);
    setAdvice(null);
    try {
      const res = await api.generateAdvice(selectedGuru, summary || undefined);
      setAdvice(res);
    } catch (err) {
      console.error("Failed to generate AI advice", err);
    } finally {
      setLoading(false);
    }
  };

  const activeGuru = gurus.find((g) => g.id === selectedGuru) || gurus[0] || GURUS[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl flex items-center gap-2">
          <span>AI Financial Advisor</span>
          <Badge variant="teal">AI Engine</Badge>
        </h1>
        <p className="text-sm text-slate-400">
          Personalized spending analysis and actionable financial recommendations framed through legendary investment philosophies.
        </p>
      </div>

      {/* Spending Snapshot */}
      <div>
        <h3 className="mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Your Financial Snapshot
        </h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
          <Card className="p-4 border-slate-800">
            <span className="text-xs text-slate-400">Total Spent</span>
            <div className="mt-1.5 text-xl font-bold text-slate-100">
              {formatINR(summary?.total_spending || 0)}
            </div>
            <p className="mt-1 text-[11px] text-slate-500">All-time recorded</p>
          </Card>

          <Card className="p-4 border-slate-800">
            <span className="text-xs text-slate-400">This Month</span>
            <div className="mt-1.5 text-xl font-bold text-teal-400">
              {formatINR(summary?.monthly_spending || 0)}
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Current cycle</p>
          </Card>

          <Card className="p-4 border-slate-800">
            <span className="text-xs text-slate-400">Top Category</span>
            <div className="mt-1.5 truncate text-lg font-bold text-amber-300">
              {summary?.top_category || "N/A"}
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Highest volume spend</p>
          </Card>

          <Card className="p-4 border-slate-800">
            <span className="text-xs text-slate-400">Est. Monthly Savings</span>
            <div className="mt-1.5 text-xl font-bold text-emerald-400">
              {formatINR(budgetData?.savings_estimate || 0)}
            </div>
            <p className="mt-1 text-[11px] text-slate-500">Income - monthly spend</p>
          </Card>
        </div>
      </div>

      {/* Guru Philosophy Selector Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Choose Advisory Philosophy
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {gurus.map((guru) => {
            const isSelected = selectedGuru === guru.id;
            return (
              <div
                key={guru.id}
                onClick={() => {
                  setSelectedGuru(guru.id);
                  setAdvice(null);
                }}
                className={`cursor-pointer rounded-xl border p-4 transition-all duration-200 ${
                  isSelected
                    ? "bg-slate-900 border-teal-500/80 shadow-[0_0_20px_-5px_rgba(20,184,166,0.25)] ring-1 ring-teal-500"
                    : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
                }`}
              >
                <div className="text-3xl mb-2">{guru.emoji}</div>
                <h4 className="text-sm font-bold text-slate-100">{guru.name}</h4>
                <p className="mt-1.5 text-xs text-slate-400 leading-relaxed">
                  {guru.tagline}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Button */}
      <div className="flex justify-center pt-2">
        <Button
          size="lg"
          variant="primary"
          onClick={handleGenerateAdvice}
          isLoading={loading}
          className="px-8 shadow-lg shadow-teal-500/20"
        >
          <Sparkles className="h-4 w-4" />
          <span>Analyze Finances with {activeGuru.name}</span>
        </Button>
      </div>

      {/* AI Advice Output Display */}
      {advice && (
        <div className="space-y-4 pt-2 animate-in fade-in slide-in-from-bottom-3 duration-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{activeGuru.emoji}</span>
              <div>
                <h3 className="text-base font-bold text-slate-100">{activeGuru.name} AI Analysis</h3>
                <p className="text-xs text-slate-400">Customized to your active spending profile</p>
              </div>
            </div>
            {advice._mock && (
              <Badge variant="yellow">Offline Knowledge Mode</Badge>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {/* Observation */}
            <Card className="p-5 border-slate-800 space-y-2 bg-slate-900/90">
              <div className="flex items-center gap-2 text-sm font-bold text-teal-300">
                <Lightbulb className="h-4 w-4 text-teal-400" />
                <span>Spending Observation</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{advice.observation}</p>
            </Card>

            {/* Recommendation */}
            <Card className="p-5 border-slate-800 space-y-2 bg-slate-900/90">
              <div className="flex items-center gap-2 text-sm font-bold text-sky-300">
                <Sparkles className="h-4 w-4 text-sky-400" />
                <span>Core Recommendation</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{advice.recommendation}</p>
            </Card>

            {/* Why? */}
            <Card className="p-5 border-slate-800 space-y-2 bg-slate-900/90">
              <div className="flex items-center gap-2 text-sm font-bold text-purple-300">
                <HelpCircle className="h-4 w-4 text-purple-400" />
                <span>Philosophy & Rationale</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{advice.why}</p>
            </Card>

            {/* Action */}
            <Card className="p-5 border-teal-500/30 space-y-2 bg-gradient-to-br from-slate-900 to-teal-950/20">
              <div className="flex items-center gap-2 text-sm font-bold text-emerald-300">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>Concrete Action This Week</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-medium">
                {advice.action}
              </p>
            </Card>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="flex items-start gap-2.5 rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 text-xs text-slate-400">
        <ShieldAlert className="h-4 w-4 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-300">Disclaimer:</strong> FinMate AI provides educational insights based on your entered transactions and universal financial philosophies. This does not constitute SEBI-registered investment advice.
        </div>
      </div>
    </div>
  );
}
