"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileImage,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  PlusCircle,
  Download,
  Sparkles,
  RefreshCw,
  Receipt,
  ScanLine,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import {
  CATEGORIES,
  PAYMENT_METHODS,
  formatINR,
} from "@/lib/utils";
import { ExpenseInput, OCRResult } from "@/types";

export default function UploadPage() {
  const [activeTab, setActiveTab] = useState<"ocr" | "manual" | "csv">("ocr");

  // OCR State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [ocrFormData, setOcrFormData] = useState<ExpenseInput>({
    merchant: "",
    amount: 0,
    date: new Date().toISOString().split("T")[0],
    category: "Food & Dining",
    payment: "UPI",
    notes: "",
  });
  const [ocrSaved, setOcrSaved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Manual State
  const [manualFormData, setManualFormData] = useState<ExpenseInput>({
    merchant: "",
    amount: 0,
    date: new Date().toISOString().split("T")[0],
    category: "Food & Dining",
    payment: "UPI",
    notes: "",
  });
  const [manualSaving, setManualSaving] = useState(false);
  const [manualSuccess, setManualSuccess] = useState(false);

  // CSV State
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvPreview, setCsvPreview] = useState<Array<Record<string, any>>>([]);
  const [csvImporting, setCsvImporting] = useState(false);
  const [csvResultMsg, setCsvResultMsg] = useState<string | null>(null);

  // Handle OCR file drop/select
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
    setOcrLoading(true);
    setOcrResult(null);
    setOcrSaved(false);

    try {
      const result = await api.scanReceipt(file);
      setOcrResult(result);

      // Auto-categorize if merchant detected
      let cat = "Others";
      if (result.merchant) {
        const catRes = await api.autoCategorize(result.merchant);
        cat = catRes.category;
      }

      setOcrFormData({
        merchant: result.merchant || "",
        amount: result.amount || 0,
        date: result.date || new Date().toISOString().split("T")[0],
        category: cat,
        payment: result.payment_method || "UPI",
        notes: result.transaction_type ? `OCR detected: ${result.transaction_type}` : "Extracted via OCR",
      });
    } catch (err) {
      console.error("OCR scan failed", err);
    } finally {
      setOcrLoading(false);
    }
  };

  const handleSaveOcrExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ocrFormData.merchant.trim() || ocrFormData.amount <= 0) return;

    try {
      await api.createExpense(ocrFormData);
      setOcrSaved(true);
    } catch (err) {
      console.error("Failed to save OCR expense", err);
    }
  };

  const handleSaveManualExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualFormData.merchant.trim() || manualFormData.amount <= 0) return;

    setManualSaving(true);
    try {
      await api.createExpense(manualFormData);
      setManualSuccess(true);
      setManualFormData({
        merchant: "",
        amount: 0,
        date: new Date().toISOString().split("T")[0],
        category: "Food & Dining",
        payment: "UPI",
        notes: "",
      });
      setTimeout(() => setManualSuccess(false), 4000);
    } catch (err) {
      console.error("Failed to create manual expense", err);
    } finally {
      setManualSaving(false);
    }
  };

  // CSV parsing preview
  const handleCsvSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCsvFile(file);
    setCsvResultMsg(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split("\n").filter((l) => l.trim().length > 0);
      if (lines.length > 1) {
        const headers = lines[0].split(",").map((h) => h.trim().replace(/"/g, ""));
        const rows = lines.slice(1, 6).map((line) => {
          const vals = line.split(",").map((v) => v.trim().replace(/"/g, ""));
          const obj: Record<string, any> = {};
          headers.forEach((h, i) => {
            obj[h] = vals[i] || "";
          });
          return obj;
        });
        setCsvPreview(rows);
      }
    };
    reader.readAsText(file);
  };

  const handleImportCsv = async () => {
    if (!csvFile) return;
    setCsvImporting(true);
    try {
      const res = await api.importCsv(csvFile);
      setCsvResultMsg(res.message);
      setCsvFile(null);
      setCsvPreview([]);
    } catch (err: any) {
      setCsvResultMsg(err?.message || "Failed to import CSV");
    } finally {
      setCsvImporting(false);
    }
  };

  const downloadSampleCsv = () => {
    const sample = "merchant,amount,date,category,payment,notes\nSwiggy,540,2026-09-20,Food & Dining,UPI,Dinner\nUber,320,2026-09-19,Transport,UPI,Cab\nAmazon,2499,2026-09-18,Shopping,Credit Card,Headphones\n";
    const blob = new Blob([sample], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "finmate_sample_import.csv";
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Add & Upload Expenses
        </h1>
        <p className="text-sm text-slate-400">
          Upload receipt screenshots with AI OCR, record transactions manually, or bulk import bank CSVs.
        </p>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab("ocr")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "ocr"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <ScanLine className="h-4 w-4" />
          <span>Receipt & Screenshot OCR</span>
        </button>
        <button
          onClick={() => setActiveTab("manual")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "manual"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <PlusCircle className="h-4 w-4" />
          <span>Manual Entry</span>
        </button>
        <button
          onClick={() => setActiveTab("csv")}
          className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-semibold transition-colors ${
            activeTab === "csv"
              ? "border-teal-400 text-teal-300"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileSpreadsheet className="h-4 w-4" />
          <span>CSV Bulk Import</span>
        </button>
      </div>

      {/* ── TAB 1: OCR Upload ────────────────────────────────────────── */}
      {activeTab === "ocr" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          {/* Left Column: Dropzone & Image Preview */}
          <div className="lg:col-span-6 space-y-4">
            <Card className="p-5 border-slate-800">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
              />

              {!imagePreview ? (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const file = e.dataTransfer.files?.[0];
                    if (file) handleFileSelect(file);
                  }}
                  className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-teal-500/40 bg-teal-500/5 p-10 text-center cursor-pointer hover:bg-teal-500/10 hover:border-teal-400 transition-all group"
                >
                  <div className="rounded-full bg-teal-500/10 p-4 text-teal-400 group-hover:scale-110 transition-transform">
                    <UploadCloud className="h-8 w-8" />
                  </div>
                  <h4 className="mt-3 text-sm font-semibold text-slate-200">
                    Click to upload or drag & drop receipt
                  </h4>
                  <p className="mt-1 text-xs text-slate-400">
                    Supports UPI screenshots (GPay, PhonePe, Paytm), bills & physical receipts (PNG, JPG)
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-slate-950 max-h-[380px] flex items-center justify-center">
                    <img
                      src={imagePreview}
                      alt="Receipt preview"
                      className="max-h-[380px] w-auto object-contain"
                    />
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400 truncate max-w-[200px]">
                      {selectedFile?.name}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <RefreshCw className="h-3.5 w-3.5" /> Re-upload Image
                    </Button>
                  </div>
                </div>
              )}
            </Card>

            {/* OCR Engine Info */}
            <div className="flex items-center gap-2 rounded-xl bg-slate-900/60 border border-slate-800 p-3 text-xs text-slate-400">
              <Sparkles className="h-4 w-4 text-teal-400 shrink-0" />
              <span>
                Powered by <strong>Gemini Vision 2.0 Flash</strong> & Tesseract OCR pipeline for Indian financial screenshots.
              </span>
            </div>
          </div>

          {/* Right Column: OCR Extraction & Review Form */}
          <div className="lg:col-span-6">
            <Card className="p-6 border-slate-800 h-full flex flex-col justify-between">
              <div>
                <CardHeader className="mb-4">
                  <div>
                    <CardTitle>OCR Review Screen</CardTitle>
                    <p className="text-xs text-slate-400">
                      Verify extracted details before saving to your records
                    </p>
                  </div>
                  {ocrResult && (
                    <Badge variant={ocrResult.confidence > 0.7 ? "green" : "yellow"}>
                      {(ocrResult.confidence * 100).toFixed(0)}% Confidence
                    </Badge>
                  )}
                </CardHeader>

                {ocrLoading ? (
                  <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
                    <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
                    <p className="text-sm font-semibold text-slate-200">
                      Analyzing screenshot with OCR...
                    </p>
                    <p className="text-xs text-slate-400">
                      Extracting merchant name, amount, date, and payment method
                    </p>
                  </div>
                ) : !selectedFile ? (
                  <div className="flex flex-col items-center justify-center py-16 text-center text-slate-500">
                    <Receipt className="h-10 w-10 mb-2 opacity-40" />
                    <p className="text-sm">Upload an image on the left to begin extraction</p>
                  </div>
                ) : (
                  <form onSubmit={handleSaveOcrExpense} className="space-y-4">
                    {ocrSaved ? (
                      <div className="flex flex-col items-center justify-center py-10 text-center space-y-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-6">
                        <CheckCircle2 className="h-10 w-10 text-emerald-400" />
                        <h4 className="text-base font-bold text-slate-100">
                          Expense Saved Successfully!
                        </h4>
                        <p className="text-xs text-slate-300">
                          {ocrFormData.merchant} — {formatINR(ocrFormData.amount, 2)} has been recorded.
                        </p>
                        <Button
                          type="button"
                          variant="primary"
                          size="sm"
                          onClick={() => {
                            setSelectedFile(null);
                            setImagePreview(null);
                            setOcrResult(null);
                            setOcrSaved(false);
                          }}
                        >
                          Scan Another Receipt
                        </Button>
                      </div>
                    ) : (
                      <>
                        <Input
                          label="Merchant / Payee *"
                          value={ocrFormData.merchant}
                          onChange={(e) =>
                            setOcrFormData({ ...ocrFormData, merchant: e.target.value })
                          }
                          placeholder="e.g. Swiggy, Uber, Zomato"
                          required
                        />

                        <div className="grid grid-cols-2 gap-3">
                          <Input
                            label="Amount (₹) *"
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={ocrFormData.amount || ""}
                            onChange={(e) =>
                              setOcrFormData({
                                ...ocrFormData,
                                amount: parseFloat(e.target.value) || 0,
                              })
                            }
                            required
                          />
                          <Input
                            label="Date *"
                            type="date"
                            value={ocrFormData.date}
                            onChange={(e) =>
                              setOcrFormData({ ...ocrFormData, date: e.target.value })
                            }
                            required
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <Select
                            label="Category *"
                            value={ocrFormData.category}
                            onChange={(e) =>
                              setOcrFormData({ ...ocrFormData, category: e.target.value })
                            }
                          >
                            {CATEGORIES.map((cat) => (
                              <option key={cat} value={cat}>
                                {cat}
                              </option>
                            ))}
                          </Select>

                          <Select
                            label="Payment Method *"
                            value={ocrFormData.payment}
                            onChange={(e) =>
                              setOcrFormData({ ...ocrFormData, payment: e.target.value })
                            }
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
                          value={ocrFormData.notes || ""}
                          onChange={(e) =>
                            setOcrFormData({ ...ocrFormData, notes: e.target.value })
                          }
                        />

                        <div className="pt-2">
                          <Button type="submit" variant="primary" className="w-full">
                            Confirm & Save Expense
                          </Button>
                        </div>
                      </>
                    )}
                  </form>
                )}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* ── TAB 2: Manual Entry ──────────────────────────────────────── */}
      {activeTab === "manual" && (
        <Card className="max-w-2xl mx-auto p-6 border-slate-800">
          <CardHeader className="mb-4">
            <div>
              <CardTitle>Manual Expense Entry</CardTitle>
              <p className="text-xs text-slate-400">
                Directly add an expense to your database
              </p>
            </div>
          </CardHeader>

          {manualSuccess && (
            <div className="mb-4 flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Expense added successfully!</span>
            </div>
          )}

          <form onSubmit={handleSaveManualExpense} className="space-y-4">
            <Input
              label="Merchant / Payee Name *"
              placeholder="e.g. Swiggy, Amazon, DMart"
              value={manualFormData.merchant}
              onChange={(e) =>
                setManualFormData({ ...manualFormData, merchant: e.target.value })
              }
              required
            />

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Amount (₹) *"
                type="number"
                step="0.01"
                min="0.01"
                placeholder="450.00"
                value={manualFormData.amount || ""}
                onChange={(e) =>
                  setManualFormData({
                    ...manualFormData,
                    amount: parseFloat(e.target.value) || 0,
                  })
                }
                required
              />
              <Input
                label="Date *"
                type="date"
                value={manualFormData.date}
                onChange={(e) =>
                  setManualFormData({ ...manualFormData, date: e.target.value })
                }
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Select
                label="Category *"
                value={manualFormData.category}
                onChange={(e) =>
                  setManualFormData({ ...manualFormData, category: e.target.value })
                }
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </Select>

              <Select
                label="Payment Method *"
                value={manualFormData.payment}
                onChange={(e) =>
                  setManualFormData({ ...manualFormData, payment: e.target.value })
                }
              >
                {PAYMENT_METHODS.map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </Select>
            </div>

            <Input
              label="Notes"
              placeholder="Optional description"
              value={manualFormData.notes || ""}
              onChange={(e) =>
                setManualFormData({ ...manualFormData, notes: e.target.value })
              }
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={manualSaving}
            >
              Save Expense
            </Button>
          </form>
        </Card>
      )}

      {/* ── TAB 3: CSV Import ────────────────────────────────────────── */}
      {activeTab === "csv" && (
        <div className="max-w-3xl mx-auto space-y-6">
          <Card className="p-6 border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle>Bulk Import Transactions (CSV)</CardTitle>
                <p className="text-xs text-slate-400">
                  Upload a statement export or CSV file from your bank/app
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={downloadSampleCsv}>
                <Download className="h-3.5 w-3.5" /> Sample CSV
              </Button>
            </div>

            <div className="rounded-xl border-2 border-dashed border-slate-800 p-8 text-center bg-slate-950/40">
              <input
                type="file"
                accept=".csv"
                id="csv_upload_input"
                className="hidden"
                onChange={handleCsvSelect}
              />
              <label
                htmlFor="csv_upload_input"
                className="flex flex-col items-center justify-center cursor-pointer space-y-2"
              >
                <FileSpreadsheet className="h-10 w-10 text-teal-400" />
                <span className="text-sm font-semibold text-slate-200">
                  {csvFile ? csvFile.name : "Select CSV File to Upload"}
                </span>
                <span className="text-xs text-slate-500">
                  Expected columns: merchant, amount, date, category, payment, notes
                </span>
              </label>
            </div>

            {csvResultMsg && (
              <div className="mt-4 p-3 rounded-lg bg-teal-500/10 border border-teal-500/20 text-xs text-teal-300">
                {csvResultMsg}
              </div>
            )}
          </Card>

          {csvPreview.length > 0 && (
            <Card className="p-5 border-slate-800">
              <CardTitle className="mb-3 text-sm">File Preview (First 5 Rows)</CardTitle>
              <div className="overflow-x-auto rounded-lg border border-slate-800">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 font-semibold text-slate-400 border-b border-slate-800">
                    <tr>
                      {Object.keys(csvPreview[0]).map((h) => (
                        <th key={h} className="p-2.5">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {csvPreview.map((row, i) => (
                      <tr key={i} className="hover:bg-slate-900/50">
                        {Object.values(row).map((val: any, j) => (
                          <td key={j} className="p-2.5">
                            {val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex justify-end">
                <Button
                  variant="primary"
                  onClick={handleImportCsv}
                  isLoading={csvImporting}
                >
                  Import All Transactions
                </Button>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
