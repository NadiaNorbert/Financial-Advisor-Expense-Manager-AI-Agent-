# 💎 FinMate AI

<div align="center">

## 🤖 AI-Powered Personal Finance Assistant

**Smart Expense Manager · Financial Advisor · Budget & Goals Tracker**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38BDF8?logo=tailwind-css)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-Data_Visualization-FF6384?logo=chart.js)](https://www.chartjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

<br/>

**Track your money · Understand your spending · Make smarter financial decisions**

</div>

---

## 🌟 Overview

**FinMate AI** is an AI-powered personal finance management platform designed to help users track expenses, monitor budgets, achieve savings goals, split shared group bills, and receive actionable financial advice framed around legendary wealth principles.

FinMate AI supports both:
- **Production Full-Stack Web Application (Next.js App Router + FastAPI)**
- **Streamlit Prototype (Track A)**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🏠 **Interactive Dashboard** | Real-time overview with KPI cards, monthly budget health progress bar, category distribution donut, 12-month spending history, and 60-day momentum line. |
| 💳 **Expense Management** | Live search, category and date filters, cards/table view toggle, add/edit/delete transactions with live merchant auto-categorization, and CSV export. |
| 📸 **Smart Receipt OCR** | Drag-and-drop receipt/bill scanner with auto-extraction of merchant, amount, date, and payment method via Gemini Vision & Tesseract OCR. |
| 📊 **Financial Analytics** | Deep category-wise breakdown, monthly spending trend bars, daily spending timeline, and payment method distribution. |
| 🤖 **AI Financial Advisor** | Real-time AI advisory engine offering tailored insights based on your actual spending patterns through 4 philosophies: *Warren Buffett*, *Robert Kiyosaki*, *Ramit Sethi*, and *General Financial Principles*. |
| 💰 **Budget Management** | Category-by-category spending limits with live visual health meters and instant alert badges (*On Track*, *Near Limit*, *Over Budget*). |
| 🎯 **Savings Goals** | Set milestone targets with deadlines, track accumulated savings, and view progress on half-donut gauge meters. |
| 👥 **Split Shared Expenses** | Equal and custom bill splitter with 1-click **"Import My Share"** directly into personal expense tracker. |
| 📄 **Reports & Export** | One-click export for Expenses (CSV), Budget (CSV), Goals (CSV), and Full Summary (TXT). |

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`

---

### 2. Backend Setup (FastAPI)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment variables (copy example)
cp .env.example .env

# 3. Start FastAPI server
python -m uvicorn backend.server:app --reload --port 8000
```

- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### 3. Frontend Setup (Next.js App Router)

```bash
# 1. Navigate to frontend directory
cd frontend-next

# 2. Install Node dependencies
npm install

# 3. Start development server
npm run dev
```

- **Web Application**: [http://localhost:3000](http://localhost:3000)
- **Production Build**: `npm run build`

---

### 4. Running Streamlit Prototype (Track A)

```bash
streamlit run app.py
```

---

## 🧪 Running Automated Tests

```bash
# Run all unit and integration tests (27/27 tests)
python -m pytest tests/ -v

# Run with test coverage report
python -m pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 🔐 Privacy & Security

- **Local & Private**: All data is stored locally in SQLite (`financial_advisor.db`).
- **Encrypted Credentials**: Passwords are secure-hashed using `bcrypt` and authenticated via signed JWT tokens.
- **Zero In-Memory Storage of Receipts**: Uploaded bill screenshots are processed in memory and not persisted on disk.
- **Environment Isolation**: API keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`) are loaded securely from `.env`.

---

<div align="center">

Built with ❤️ using **Next.js · React · TypeScript · Tailwind CSS · Chart.js · FastAPI · Python**

</div>
