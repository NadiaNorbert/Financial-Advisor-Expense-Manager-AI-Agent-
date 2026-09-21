"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      await api.register(username, email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Failed to create account");
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
            ✨
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">
            Create Free Account
          </h1>
          <p className="text-xs text-slate-400">
            Get started with FinMate AI Financial Assistant
          </p>
        </div>

        {/* Register Box */}
        <Card className="p-6 sm:p-8 border-slate-800 space-y-5 bg-slate-900/90 shadow-2xl">
          {error && (
            <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-400">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <Input
              label="Username *"
              placeholder="e.g. arjun_sharma"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <Input
              label="Email Address *"
              type="email"
              placeholder="arjun@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="Password *"
              type="password"
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Input
              label="Confirm Password *"
              type="password"
              placeholder="Repeat password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={loading}
            >
              Create Account <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <div className="text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-bold text-teal-400 hover:text-teal-300 underline"
            >
              Sign in
            </Link>
          </div>
        </Card>

        <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
          <span>Local storage encryption • Your data stays on your device</span>
        </div>
      </div>
    </div>
  );
}
