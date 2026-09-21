import React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading, disabled, children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-teal-500/50 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg active:scale-[0.98]";

    const variants = {
      primary:
        "bg-gradient-to-r from-teal-500 to-emerald-600 text-slate-950 font-semibold shadow-md shadow-teal-500/20 hover:from-teal-400 hover:to-emerald-500 hover:shadow-teal-500/30",
      secondary:
        "bg-slate-800 text-slate-100 hover:bg-slate-700 border border-slate-700/60",
      outline:
        "border border-slate-700 text-slate-300 hover:border-teal-500/50 hover:text-teal-400 hover:bg-teal-500/5",
      danger:
        "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 hover:border-red-500/40",
      ghost:
        "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60",
    };

    const sizes = {
      sm: "text-xs px-3 py-1.5 gap-1.5",
      md: "text-sm px-4 py-2 gap-2",
      lg: "text-base px-5 py-2.5 gap-2.5",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading && (
          <svg className="h-4 w-4 animate-spin text-current" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
