import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "teal" | "blue" | "green" | "yellow" | "red" | "purple" | "slate";
}

export function Badge({ className, variant = "slate", children, ...props }: BadgeProps) {
  const variants = {
    teal: "bg-teal-500/10 text-teal-400 border-teal-500/20",
    blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    green: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    yellow: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    red: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    slate: "bg-slate-800 text-slate-300 border-slate-700/60",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
