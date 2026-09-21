import React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, type = "text", ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="block text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <input
          type={type}
          ref={ref}
          className={cn(
            "w-full rounded-lg border border-slate-700/80 bg-slate-950/60 px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 disabled:opacity-50",
            error && "border-red-500/80 focus:border-red-500 focus:ring-red-500",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
        {helperText && !error && <p className="text-xs text-slate-500">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, children, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="block text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={cn(
            "w-full rounded-lg border border-slate-700/80 bg-slate-950/60 px-3.5 py-2 text-sm text-slate-100 transition-colors focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 disabled:opacity-50",
            error && "border-red-500/80 focus:border-red-500 focus:ring-red-500",
            className
          )}
          {...props}
        >
          {children}
        </select>
        {error && <p className="text-xs text-red-400">{error}</p>}
      </div>
    );
  }
);

Select.displayName = "Select";
