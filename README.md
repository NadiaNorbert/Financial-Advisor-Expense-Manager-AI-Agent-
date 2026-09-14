# 💎 FinMate AI

<div align="center">

## 🤖 AI-Powered Personal Finance Assistant

**Track B — Advanced Financial Advisor & Expense Manager AI Agent**

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38BDF8?logo=tailwind-css)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-Data_Visualization-FF6384?logo=chart.js)](https://www.chartjs.org/)
[![Python](https://img.shields.io/badge/Python-Backend-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

<br/>

**Track your money · Understand your spending · Make smarter financial decisions**

</div>

---

## 🌟 Overview

**FinMate AI** is an AI-powered personal finance management platform designed to help users manage their expenses, monitor budgets, track financial goals, and receive intelligent financial insights.

The project is being developed as an evolution from a **Streamlit-based financial management application (Track A)** into a modern, scalable web application using **Next.js, React, Tailwind CSS, and Chart.js (Track B)**.

FinMate AI combines financial tracking with AI-powered insights to provide users with a smarter and more interactive way to understand their financial habits.

---

# 🚀 Track A → Track B Evolution

FinMate AI began as **Track A**, a functional financial advisor and expense manager built using Streamlit.

Track B represents the next stage of the project, focusing on a modern web architecture, improved UI/UX, scalability, reusable components, and richer financial visualizations.

| Feature               | 🟢 Track A           | 🔵 Track B                       |
| --------------------- | -------------------- | -------------------------------- |
| Frontend              | Streamlit            | Next.js + React                  |
| Styling               | Streamlit Components | Tailwind CSS                     |
| UI Architecture       | Page-based Python UI | Reusable React Components        |
| Charts                | Plotly               | Chart.js                         |
| Responsiveness        | Basic                | Fully Responsive                 |
| Component Reusability | Limited              | High                             |
| API Integration       | Python Adapter Layer | REST API Service Layer           |
| UI/UX                 | Functional Dashboard | Modern Web Application           |
| Scalability           | Prototype Level      | Production-Oriented Architecture |
| Backend Integration   | Python Modules       | API-Based Architecture           |

### 🛣 Evolution Journey

```text
                    ┌─────────────────────┐
                    │      TRACK A        │
                    │                     │
                    │     Streamlit       │
                    │   Python Frontend   │
                    │   Plotly Charts     │
                    │    Mock Backend     │
                    └──────────┬──────────┘
                               │
                               │  Project Evolution
                               ▼
                    ┌─────────────────────┐
                    │      TRACK B        │
                    │                     │
                    │      Next.js        │
                    │       React         │
                    │    Tailwind CSS     │
                    │      Chart.js       │
                    │   REST API Layer    │
                    └─────────────────────┘
```

---

# ✨ Features

FinMate AI provides a complete personal finance management experience.

| Feature                        | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| 🏠 **Dashboard**               | Financial overview with income, expenses, savings, and KPIs |
| 💳 **Expense Management**      | Add, edit, delete, search, and filter transactions          |
| 📸 **Smart Expense Upload**    | OCR-based extraction from bills and receipts                |
| 📊 **Financial Analytics**     | Interactive spending and financial visualizations           |
| 🤖 **AI Financial Advisor**    | Personalized financial insights and recommendations         |
| 💰 **Budget Management**       | Create and monitor category-wise budgets                    |
| 🎯 **Financial Goals**         | Track savings goals and progress                            |
| 📈 **Spending Trends**         | Analyze financial patterns over time                        |
| 🏷️ **Expense Categorization** | Organize transactions into categories                       |
| 👥 **Shared Expenses**         | Manage shared financial expenses                            |
| 📄 **Reports**                 | Generate financial summaries and reports                    |

---

# 🖼️ Application Preview

> 📌 Screenshots will be added as Track B development progresses.

## 🏠 Dashboard

<p align="center">

![Dashboard Preview](./public/screenshots/dashboard.png)

</p>

> **Coming Soon:** Financial overview, KPI cards, recent transactions, and spending summaries.

---

## 💳 Expense Management

<p align="center">

![Expenses Preview](./public/screenshots/expenses.png)

</p>

> **Coming Soon:** Add, edit, delete, search, and filter expenses.

---

## 📊 Financial Analytics

<p align="center">

![Analytics Preview](./public/screenshots/analytics.png)

</p>

> **Coming Soon:** Category analysis, monthly spending, trends, and budget comparisons.

---

## 🤖 AI Financial Advisor

<p align="center">

![AI Advisor Preview](./public/screenshots/advisor.png)

</p>

> **Coming Soon:** AI-powered insights and personalized financial recommendations.

---

## 💰 Budget Management

<p align="center">

![Budget Preview](./public/screenshots/budget.png)

</p>

> **Coming Soon:** Category budgets and budget versus actual spending analysis.

---

# 🛠️ Technology Stack

## 🎨 Frontend

| Technology           | Purpose                           |
| -------------------- | --------------------------------- |
| **Next.js**          | Full-stack React framework        |
| **React**            | Component-based UI development    |
| **Tailwind CSS**     | Responsive and modern styling     |
| **Chart.js**         | Financial data visualization      |
| **React Chart.js 2** | Chart.js integration with React   |
| **TypeScript**       | Type-safe application development |

## ⚙️ Backend

The backend architecture can support:

* 🐍 Python
* ⚡ FastAPI
* 🤖 AI / LLM Integration
* 📸 OCR Processing
* 🧠 Financial Analysis Engine
* 🔌 REST APIs

## 🗄️ Database

Supported database options:

* PostgreSQL
* SQLite for development

---

# 🏗️ System Architecture

FinMate AI follows a modern client-server architecture.

```text
                           ┌───────────────────────┐
                           │        USER           │
                           │  Web / Mobile Browser │
                           └───────────┬───────────┘
                                       │
                                       ▼
                    ┌────────────────────────────────┐
                    │         NEXT.JS FRONTEND        │
                    │                                │
                    │  ┌──────────┐ ┌─────────────┐  │
                    │  │Dashboard │ │  Expenses   │  │
                    │  └──────────┘ └─────────────┘  │
                    │                                │
                    │  ┌──────────┐ ┌─────────────┐  │
                    │  │Analytics │ │   Budget    │  │
                    │  └──────────┘ └─────────────┘  │
                    │                                │
                    │  ┌──────────┐ ┌─────────────┐  │
                    │  │  Goals   │ │ AI Advisor  │  │
                    │  └──────────┘ └─────────────┘  │
                    └───────────────┬────────────────┘
                                    │
                                    │ REST API
                                    ▼
                    ┌────────────────────────────────┐
                    │        BACKEND SERVICES         │
                    │                                │
                    │  Expense Management Engine     │
                    │  OCR Processing                │
                    │  AI Financial Advisor          │
                    │  Budget Engine                 │
                    │  Goal Management               │
                    │  Financial Analytics           │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │           DATABASE             │
                    │                                │
                    │   Expenses │ Budgets │ Goals   │
                    └────────────────────────────────┘
```

---

# 📁 Project Structure

```text
finmate-ai/
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   │
│   ├── dashboard/
│   │   └── page.tsx
│   │
│   ├── expenses/
│   │   └── page.tsx
│   │
│   ├── analytics/
│   │   └── page.tsx
│   │
│   ├── budget/
│   │   └── page.tsx
│   │
│   ├── goals/
│   │   └── page.tsx
│   │
│   ├── advisor/
│   │   └── page.tsx
│   │
│   └── reports/
│       └── page.tsx
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Navbar.tsx
│   │   └── DashboardLayout.tsx
│   │
│   ├── dashboard/
│   │   ├── StatCard.tsx
│   │   ├── RecentTransactions.tsx
│   │   └── BudgetOverview.tsx
│   │
│   ├── charts/
│   │   ├── ExpensePieChart.tsx
│   │   ├── SpendingBarChart.tsx
│   │   ├── SpendingTrendChart.tsx
│   │   └── BudgetChart.tsx
│   │
│   └── ui/
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── Input.tsx
│       └── Modal.tsx
│
├── services/
│   ├── expenseService.ts
│   ├── budgetService.ts
│   ├── goalService.ts
│   └── advisorService.ts
│
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── constants.ts
│
├── types/
│   ├── expense.ts
│   ├── budget.ts
│   └── goal.ts
│
├── public/
│   ├── assets/
│   └── screenshots/
│       ├── dashboard.png
│       ├── expenses.png
│       ├── analytics.png
│       ├── advisor.png
│       └── budget.png
│
├── styles/
│   └── globals.css
│
├── .env.example
├── package.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have the following installed:

* Node.js 18 or higher
* npm or yarn
* Git

---

## 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd finmate-ai
```

---

## 2️⃣ Install Dependencies

```bash
npm install
```

---

## 3️⃣ Configure Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 4️⃣ Run the Development Server

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# 📊 Financial Visualizations

FinMate AI uses **Chart.js** to transform financial data into meaningful visual insights.

### 🥧 Expense Distribution

Visualizes spending across categories.

### 📊 Monthly Spending

Compares financial activity across different months.

### 📈 Spending Trends

Tracks how expenses change over time.

### 💰 Budget vs Actual

Compares planned budgets against actual spending.

### 🎯 Goal Progress

Displays the user's progress toward financial goals.

---

# 🔌 API Integration

The frontend communicates with backend services through a centralized API layer.

```text
Frontend Component
        │
        ▼
Service Layer
        │
        ▼
REST API
        │
        ▼
Backend Logic
        │
        ▼
Database
```

Example:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getExpenses() {
  const response = await fetch(`${API_URL}/expenses`);

  if (!response.ok) {
    throw new Error("Failed to fetch expenses");
  }

  return response.json();
}
```

---

# 🤖 AI Financial Advisor

The AI Financial Advisor analyzes financial information and provides intelligent recommendations.

The advisor can analyze:

* 💳 Spending patterns
* 📊 Monthly expenses
* 💰 Budget usage
* 🎯 Savings goals
* 📈 Financial trends

Example insights:

> 💡 Your food expenses have increased compared to your previous spending pattern.

> ⚠️ You are approaching your monthly entertainment budget.

> 🎯 Increasing your monthly savings can help you reach your financial goal faster.

---

# 📸 Smart Expense Processing

Users can upload:

* 🧾 Bills
* 📄 Receipts
* 📱 Expense screenshots

OCR processing extracts information such as:

```text
Merchant Name
Amount
Date
Payment Method
```

The extracted information can then be reviewed and saved as a transaction.

---

# 💳 Expense Management

Users can:

* ➕ Add expenses
* ✏️ Edit transactions
* 🗑️ Delete expenses
* 🔍 Search transactions
* 🏷️ Filter by category
* 📅 Filter by date

Example data structure:

```typescript
{
  id: 1,
  title: "Restaurant",
  amount: 450,
  category: "Food",
  date: "2026-09-14",
  paymentMethod: "UPI"
}
```

---

# 💰 Budget Management

Users can create category-wise budgets.

| Category         | Monthly Budget |
| ---------------- | -------------: |
| 🍔 Food          |         ₹5,000 |
| 🚕 Transport     |         ₹2,000 |
| 🛍️ Shopping     |         ₹3,000 |
| 🎬 Entertainment |         ₹2,000 |

FinMate AI compares actual expenses with planned budgets using interactive charts.

---

# 🎯 Financial Goals

Users can create and monitor financial goals.

Example:

```text
Goal: Emergency Fund
Target Amount: ₹100,000
Current Savings: ₹65,000
Progress: 65%
```

---

# 🧪 Testing

Run tests using:

```bash
npm test
```

Additional testing tools may be integrated as the project grows.

---

# 🌐 Deployment

The Track B frontend can be deployed using:

* ▲ Vercel
* Netlify

Basic workflow:

```bash
git add .
git commit -m "Build FinMate AI Track B"
git push origin main
```

Configure environment variables on the deployment platform before production deployment.

---

# 👥 Team Responsibilities

| Area                    | Responsibility              |
| ----------------------- | --------------------------- |
| 🎨 Frontend Development | Next.js + React             |
| 💅 UI/UX Design         | Tailwind CSS                |
| 📊 Data Visualization   | Chart.js                    |
| 🔗 API Integration      | Frontend Service Layer      |
| 📱 Responsive Design    | Desktop and Mobile Support  |
| 🤖 AI Logic             | Financial Advisor           |
| 📸 OCR                  | Receipt and Bill Processing |
| 🗄️ Database            | Financial Data Storage      |
| 🧠 Analytics            | Spending Pattern Analysis   |

---

# 🗺️ Development Roadmap

### ✅ Track A

* Streamlit frontend
* Expense tracking
* Financial dashboard
* Plotly visualizations
* Mock/demo backend
* AI advisor structure
* Budget tracking
* Financial goals

### 🚧 Track B

* Next.js frontend
* React reusable components
* Tailwind CSS UI
* Chart.js financial visualizations
* Responsive design
* REST API integration
* Improved user experience

### 🔮 Future

* User authentication
* Advanced AI agents
* Expense prediction
* Smart notifications
* Voice-based expense entry
* Multi-currency support
* Mobile application
* Advanced financial forecasting

---

# 🔐 Privacy & Security

FinMate AI follows good practices for handling financial information.

* 🔒 API keys are stored using environment variables.
* 🚫 Sensitive credentials are never hard-coded.
* 🛡️ Environment files are excluded from Git repositories.
* 🔐 Backend APIs should implement authentication and authorization.
* 💾 Financial data should be securely stored.

---

# 📜 License

This project is currently developed as an **academic and portfolio project**.

A formal license can be added in future versions.

---

<div align="center">

## 💎 FinMate AI

### **Understand your money. Control your spending. Build smarter financial habits.**

**Track A → Track B 🚀**

Built with ❤️ using **Next.js · React · Tailwind CSS · Chart.js · AI**

⭐ If you like this project, consider giving the repository a star!

</div>
