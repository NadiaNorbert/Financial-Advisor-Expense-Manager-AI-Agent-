"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, ShieldCheck } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!username.trim() || !password.trim()) return;

    setLoading(true);
    try {
      await api.login(username, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-slate-950">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 text-2xl shadow-xl shadow-teal-500/20">
            💎
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">
            Sign In to FinMate <span className="text-teal-400">AI</span>
          </h1>
          <p className="text-xs text-slate-400">
            Your AI-Powered Personal Finance Assistant
          </p>
        </div>

        {/* Login Box */}
        <Card className="p-6 sm:p-8 border-slate-800 space-y-5 bg-slate-900/90 shadow-2xl">
          {error && (
            <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-400">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              label="Username"
              placeholder="e.g. arjun"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={loading}
            >
              Sign In <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <div className="text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="font-bold text-teal-400 hover:text-teal-300 underline"
            >
              Create free account
            </Link>
          </div>
        </Card>

        {/* Status */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
          <span>End-to-End Encrypted • Private & Secure</span>
        </div>
      </div>
    </div>
  );
}
