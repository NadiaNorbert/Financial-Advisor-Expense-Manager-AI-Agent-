"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ReceiptText,
  ScanLine,
  BarChart3,
  PieChart,
  Target,
  Sparkles,
  Users2,
  FileText,
  UserCheck,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Expenses", href: "/expenses", icon: ReceiptText },
  { name: "Upload & OCR", href: "/upload", icon: ScanLine },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Budget", href: "/budget", icon: PieChart },
  { name: "Savings Goals", href: "/goals", icon: Target },
  { name: "AI Advisor", href: "/advisor", icon: Sparkles, badge: "AI" },
  { name: "Split Expenses", href: "/split", icon: Users2 },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Profile", href: "/profile", icon: UserCheck },
];

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800/80 bg-slate-950/95 p-4 backdrop-blur-md transition-transform duration-300 lg:static lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Brand Logo */}
        <div className="mb-6 flex items-center gap-3 px-3 py-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 shadow-md shadow-teal-500/20">
            <span className="text-xl">💎</span>
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-slate-100">
              FinMate <span className="text-teal-400">AI</span>
            </span>
            <span className="block text-[10px] font-medium tracking-wider text-slate-400 uppercase">
              Finance Assistant
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-1 overflow-y-auto pr-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-gradient-to-r from-teal-500/15 to-emerald-500/10 text-teal-300 border border-teal-500/20 font-semibold"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={cn(
                      "h-4 w-4 transition-colors",
                      isActive
                        ? "text-teal-400"
                        : "text-slate-400 group-hover:text-slate-200"
                    )}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="rounded-full bg-teal-500/20 px-2 py-0.5 text-[10px] font-bold text-teal-300 border border-teal-500/30">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Security Status Pill */}
        <div className="mt-auto rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              <span className="font-medium text-slate-300">Private & Secure</span>
            </div>
            <ShieldCheck className="h-4 w-4 text-teal-400" />
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            Local & Cloud Encrypted
          </p>
        </div>
      </aside>
    </>
  );
}
