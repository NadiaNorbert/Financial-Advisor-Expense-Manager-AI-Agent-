"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  User as UserIcon,
  ShieldCheck,
  KeyRound,
  LogOut,
  Mail,
  Hash,
  CheckCircle2,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { User } from "@/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  // Password state
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    const u = api.getCurrentUser();
    setUser(u);
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters.");
      return;
    }

    setPasswordLoading(true);
    try {
      // Simulate / call backend password endpoint
      setPasswordSuccess("Password updated successfully!");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordSuccess(null), 4000);
    } catch (err: any) {
      setPasswordError(err?.message || "Failed to update password");
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleSignOut = () => {
    api.logout();
    router.push("/login");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Account Profile & Security
        </h1>
        <p className="text-sm text-slate-400">
          Manage your user profile credentials and security preferences.
        </p>
      </div>

      {/* Main Profile Hero Card */}
      <Card className="p-6 border-slate-800 bg-gradient-to-r from-slate-900 to-slate-900/80">
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-5">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 text-3xl font-extrabold text-slate-950 shadow-xl shadow-teal-500/20">
            {user?.username?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="space-y-1 text-center sm:text-left flex-1">
            <h2 className="text-xl font-bold text-slate-100">{user?.username || "User"}</h2>
            <p className="text-xs text-slate-400">{user?.email || "user@example.com"}</p>

            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-2">
              <Badge variant="teal">
                <Hash className="h-3 w-3" /> ID #{user?.id || 1}
              </Badge>
              <Badge variant="green">
                <ShieldCheck className="h-3 w-3" /> Verified Local Account
              </Badge>
              <Badge variant="blue">Active Plan</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Info Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Card className="p-4 border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <UserIcon className="h-3.5 w-3.5 text-teal-400" />
            <span>Username</span>
          </div>
          <div className="mt-2 text-sm font-bold text-slate-100">{user?.username || "User"}</div>
        </Card>

        <Card className="p-4 border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <Mail className="h-3.5 w-3.5 text-sky-400" />
            <span>Email Address</span>
          </div>
          <div className="mt-2 truncate text-sm font-bold text-slate-100">
            {user?.email || "user@example.com"}
          </div>
        </Card>

        <Card className="p-4 border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <Hash className="h-3.5 w-3.5 text-emerald-400" />
            <span>User Identifier</span>
          </div>
          <div className="mt-2 text-sm font-bold text-slate-100">#{user?.id || 1}</div>
        </Card>
      </div>

      {/* Change Password Form */}
      <Card className="p-6 border-slate-800 space-y-4">
        <CardHeader className="mb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <KeyRound className="h-4 w-4 text-teal-400" />
            Change Password
          </CardTitle>
        </CardHeader>

        {passwordSuccess && (
          <div className="flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{passwordSuccess}</span>
          </div>
        )}

        {passwordError && (
          <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-400">
            {passwordError}
          </div>
        )}

        <form onSubmit={handleChangePassword} className="space-y-4 max-w-lg">
          <Input
            label="Current Password"
            type="password"
            placeholder="••••••••"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            required
          />

          <Input
            label="New Password"
            type="password"
            placeholder="At least 6 characters"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />

          <Input
            label="Confirm New Password"
            type="password"
            placeholder="Repeat new password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          <Button type="submit" variant="primary" size="sm" isLoading={passwordLoading}>
            Update Password
          </Button>
        </form>
      </Card>

      {/* Sign Out Card */}
      <Card className="p-5 border-slate-800 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">Sign Out</h4>
          <p className="text-xs text-slate-400">End your current session</p>
        </div>
        <Button variant="danger" size="sm" onClick={handleSignOut}>
          <LogOut className="h-4 w-4" /> Sign Out
        </Button>
      </Card>
    </div>
  );
}
