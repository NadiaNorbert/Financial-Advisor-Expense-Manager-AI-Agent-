"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Menu, Plus, Sparkles, User as UserIcon, LogOut, Bell } from "lucide-react";
import { Button } from "@/lib/../components/ui/Button";
import { api } from "@/lib/api";
import { User } from "@/types";

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [greeting, setGreeting] = useState("Good day");
  const [todayDate, setTodayDate] = useState("");

  useEffect(() => {
    setUser(api.getCurrentUser());
    const hour = new Date().getHours();
    setGreeting(hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening");
    
    setTodayDate(
      new Date().toLocaleDateString("en-IN", {
        weekday: "short",
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    );
  }, []);

  const handleLogout = () => {
    api.logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-4 backdrop-blur-md sm:px-6">
      {/* Left side: Hamburger & Greeting */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-900 hover:text-slate-200 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <h1 className="text-sm font-semibold text-slate-100 sm:text-base">
            {greeting},{" "}
            <span className="text-teal-400">{user?.username || "User"}</span>!
          </h1>
          <p className="text-[11px] text-slate-400 sm:block hidden">{todayDate}</p>
        </div>
      </div>

      {/* Right side: Quick actions & Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        <Link href="/upload">
          <Button size="sm" variant="primary" className="shadow-none">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Add Expense</span>
          </Button>
        </Link>

        <Link href="/advisor">
          <Button size="sm" variant="outline" className="hidden sm:inline-flex border-teal-500/30 text-teal-300">
            <Sparkles className="h-3.5 w-3.5 text-teal-400" />
            <span>AI Advice</span>
          </Button>
        </Link>

        {/* Profile Pill */}
        <div className="flex items-center gap-2 border-l border-slate-800 pl-2 sm:pl-3">
          <Link
            href="/profile"
            className="flex items-center gap-2 rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs text-slate-300 transition-colors hover:bg-slate-800 hover:text-white border border-slate-800"
          >
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-teal-500/20 text-teal-300 text-[10px] font-bold">
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <span className="max-w-[100px] truncate font-medium hidden sm:inline">
              {user?.username || "User"}
            </span>
          </Link>

          <button
            onClick={handleLogout}
            title="Sign Out"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-900 hover:text-red-400"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
