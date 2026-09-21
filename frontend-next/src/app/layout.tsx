import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinMate AI – AI-Powered Personal Finance Assistant",
  description: "Track expenses, manage budgets, automate receipt OCR, and receive personalized AI financial advice.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
