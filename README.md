
# 💎 FinMate AI

<div align="center">

## 🤖 AI-Powered Personal Finance Assistant

**Smart Expense Manager · Financial Advisor · Budget & Goals Tracker**

<br/>

**Track your money · Understand your spending · Make smarter financial decisions**

</div>

---

## 🌟 Overview

**FinMate AI** is an AI-powered personal finance management platform designed to help users track expenses, monitor budgets, achieve savings goals, split shared group bills, and receive personalized financial insights.

The platform combines intelligent expense management, interactive financial visualizations, and AI-powered financial assistance to make personal finance easier to understand and manage.

FinMate AI supports both:

* **Production Full-Stack Web Application:** Next.js App Router + FastAPI

* **Streamlit Prototype:** Track A

🚧 **Development Status:** FinMate AI is actively being upgraded. We are enhancing the Chat Advisor, improving graph generation and financial visualizations, and working on fixing and optimizing pages that are not yet functioning as expected.

---

## ✨ Key Features

| Feature                             | Description                                                                                                                                                                                                                                                                             |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🏠 **Interactive Dashboard**        | Real-time overview with KPI cards, monthly budget health progress bar, category distribution donut, 12-month spending history, and 60-day spending momentum line.                                                                                                                       |
| 💳 **Expense Management**           | Live search, category and date filters, cards/table view toggle, add/edit/delete transactions with live merchant auto-categorization, and CSV export.                                                                                                                                   |
| 📸 **Smart Receipt OCR**            | Drag-and-drop receipt and bill scanner with automatic extraction of merchant, amount, date, and payment method using Gemini Vision and Tesseract OCR.                                                                                                                                   |
| 📊 **Financial Analytics & Graphs** | Visualize financial data through category-wise breakdowns, monthly spending trends, daily spending timelines, and payment method distributions. Graph generation and visualization features are being improved.                                                                         |
| 🤖 **Enhanced AI Chat Advisor**     | An AI-powered conversational financial assistant designed to provide personalized financial guidance, answer money-related questions, analyze spending patterns, and help users understand their financial data. The chat experience and response quality are currently being enhanced. |
| 💡 **AI Financial Insights**        | Receive personalized financial insights based on actual spending patterns through four philosophies: *Warren Buffett*, *Robert Kiyosaki*, *Ramit Sethi*, and *General Financial Principles*.                                                                                            |
| 💰 **Budget Management**            | Category-by-category spending limits with live visual health meters and instant alert badges: *On Track*, *Near Limit*, and *Over Budget*.                                                                                                                                              |
| 🎯 **Savings Goals**                | Set milestone targets with deadlines, track accumulated savings, and view progress through visual gauge meters.                                                                                                                                                                         |
| 👥 **Split Shared Expenses**        | Equal and custom bill splitting with one-click **Import My Share** directly into the personal expense tracker.                                                                                                                                                                          |
| 📄 **Reports & Export**             | Export expenses, budgets, and goals as CSV files, along with a complete financial summary in TXT format.                                                                                                                                                                                |

---

## 🚧 Current Development & Improvements

FinMate AI is under active development, with ongoing improvements focused on making the application more reliable, intelligent, and user-friendly.

### Current upgrade priorities

* **Chat Advisor Enhancement:** Improving conversational responses, financial data understanding, and personalized assistance.

* **Graph Generation:** Enhancing financial graph generation, data visualization, and chart accuracy.

* **Page Functionality:** Identifying and fixing issues in pages that are not working as expected.

* **UI/UX Improvements:** Refining page layouts, navigation, responsiveness, and the overall user experience.

* **Performance & Reliability:** Improving application stability and ensuring features work consistently across the platform.

Some features and pages may not work as expected while these improvements are in progress.

---

## 🚀 Quick Start

### 1. Prerequisites

* **Python 3.10+**

* **Node.js 18+** and `npm`

### 2. Backend Setup (FastAPI)

```
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment variables
cp .env.example .env

# 3. Start FastAPI server
python -m uvicorn backend.server:app --reload --port 8000
```

* **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

* **Alternative API Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

* **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

### 3. Frontend Setup (Next.js App Router)

```
# 1. Navigate to frontend directory
cd frontend-next

# 2. Install Node dependencies
npm install

# 3. Start development server
npm run dev
```

* **Web Application:** [http://localhost:3000](http://localhost:3000)

* **Production Build:** `npm run build`

### 4. Running the Streamlit Prototype (Track A)

```
streamlit run app.py
```

---

## 🧪 Running Automated Tests

```
# Run all unit and integration tests
python -m pytest tests/ -v

# Run with test coverage report
python -m pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 🔐 Privacy & Security

* **Local Data Storage:** Financial data is stored locally in SQLite (`financial_advisor.db`).

* **Password Security:** Passwords are securely hashed using bcrypt.

* **Authentication:** Signed JWT tokens are used for authentication.

* **Receipt Processing:** Uploaded receipt images are processed in memory and are not persisted on disk.

* **Environment Variables:** API keys such as `GOOGLE_API_KEY` and `OPENAI_API_KEY` are loaded from the `.env` file.

---

## 🛠️ Tech Stack

* **Frontend:** Next.js, React, TypeScript, Tailwind CSS

* **Backend:** FastAPI, Python

* **Database:** SQLite

* **AI Integration:** Gemini Vision, OpenAI, AI-powered financial assistance

* **Data Visualization:** Chart.js

* **Authentication:** JWT, bcrypt

---

## 📌 Project Status

FinMate AI is an ongoing development project. The core application includes expense tracking, budget management, savings goals, financial analytics, and AI-powered financial assistance.

We are currently focusing on enhancing the Chat Advisor, improving financial graph generation, and resolving functionality issues across certain pages.

Our goal is to deliver a more reliable, interactive, and intelligent personal finance management experience.

---

<div align="center">

Built with ❤️ using **Next.js · React · TypeScript · Tailwind CSS · Chart.js · FastAPI · Python**

</div>
