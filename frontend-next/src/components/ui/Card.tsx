import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
  hover?: boolean;
}

export function Card({ className, glow, hover, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-slate-800 bg-slate-900/80 p-5 backdrop-blur-sm transition-all duration-200",
        glow && "border-teal-500/30 shadow-[0_0_20px_-5px_rgba(20,184,166,0.15)]",
        hover && "hover:border-slate-700 hover:bg-slate-900/95 hover:shadow-lg",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("mb-4 flex items-center justify-between", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("text-base font-semibold text-slate-100", className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-xs text-slate-400", className)} {...props}>
      {children}
    </p>
  );
}
