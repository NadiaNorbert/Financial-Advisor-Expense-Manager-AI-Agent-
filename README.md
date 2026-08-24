# 💎 FinMate AI
### Your AI-Powered Personal Finance Assistant

> **Track A — Essential Financial Advisor & Expense Manager AI Agent**
> College project · Member 2 (Frontend) · Built with Streamlit

---

## 📋 Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Quick Start (Local)](#quick-start-local)
4. [Backend Integration Guide](#backend-integration-guide)
5. [Deploy to Streamlit Cloud](#deploy-to-streamlit-cloud)
6. [Environment Variables](#environment-variables)
7. [Running Tests](#running-tests)
8. [Member Responsibilities](#member-responsibilities)
9. [Mock / Demo Mode](#mock--demo-mode)

---

## Features

| Page | What it does |
|------|-------------|
| 🏠 Dashboard | KPI cards, spending charts, budget health, recent transactions |
| 📸 Upload Expense | OCR screenshot parsing, manual entry form, CSV bulk import |
| 💳 Expenses | Searchable/filterable table, inline edit & delete, export |
| 📊 Analytics | Category donut, bar, trend line, daily charts, payment breakdown |
| 💡 AI Advisor | Guru selector (Buffett / Kiyosaki / Ramit), AI advice cards |
| 💰 Budget | Per-category progress bars, budget vs actual chart, settings |
| 🎯 Goals | Savings goal tracking with gauge charts, add/edit/delete |
| 🤝 Splitwise | Shared expense viewer, import to personal tracker |
| 📄 Reports | CSV + TXT export for expenses, budget, goals, full summary |

---

## Project Structure

```
project/
├── app.py                        # Main entry point
├── requirements.txt
├── .env.example                  # Copy to .env and fill secrets
├── .streamlit/
│   └── config.toml               # Dark teal theme
│
├── frontend/
│   ├── styles.py                 # Global CSS injection
│   ├── components/
│   │   ├── sidebar.py            # Navigation + status pills
│   │   ├── metric_card.py        # KPI tile components
│   │   ├── expense_card.py       # Styled expense row cards
│   │   └── charts.py             # All Plotly chart builders
│   └── pages/
│       ├── dashboard.py
│       ├── upload_expense.py
│       ├── expenses.py
│       ├── analytics.py
│       ├── budget.py
│       ├── advisor.py
│       ├── goals.py
│       ├── splitwise.py
│       └── reports.py
│
├── backend/                      # Member 1's modules go here
│   ├── adapter.py                # ← Integration contract (read this!)
│   ├── ocr/
│   │   └── expense_ocr.py        # Member 1: extract_expense_from_image()
│   ├── expenses/
│   │   ├── categorizer.py        # Member 1: categorize_expense()
│   │   ├── crud.py               # Member 1: add/update/delete/get_all
│   │   ├── csv_importer.py       # Member 1: import_csv_expenses()
│   │   └── analyzer.py           # Member 1: get_spending_summary()
│   ├── advisor/
│   │   └── advisor.py            # Member 1: generate_financial_advice()
│   ├── budgeting/
│   │   ├── budget_engine.py      # Member 1: calculate_budget()
│   │   └── goals.py              # Member 1: get/save/update/delete goal
│   └── splitwise/
│       └── splitwise_client.py   # Member 1: get_splitwise_expenses()
│
├── utils/
│   └── export.py                 # CSV / TXT report generation
│
└── tests/
    └── test_ui_helpers.py        # Pytest unit tests
```

---

## Quick Start (Local)

### 1. Clone / download the project

```bash
git clone <repo-url>
cd project
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables (optional for mock mode)

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
# Edit .env and fill in your API keys
```

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** automatically.

> **No backend needed to run** — the app runs in demo/mock mode
> using sample data until Member 1's modules are connected.

---

## Backend Integration Guide

> **For Member 1:** Read `backend/adapter.py` — it is the full integration contract.

The adapter layer uses this pattern for every function:

```python
def some_function(args):
    # 1. Try to import and call your real implementation
    real_fn = _try_import("backend.your_module", "your_function")
    if real_fn:
        return real_fn(args)
    # 2. Fall back to mock if your module doesn't exist yet
    return mock_result
```

### Adding your implementations

Place your files in the correct `backend/` subdirectory and match these signatures exactly:

#### OCR — `backend/ocr/expense_ocr.py`
```python
def extract_expense_from_image(image_bytes: bytes) -> dict:
    # Returns: {merchant, amount, date, payment_method, confidence, raw_text}
```

#### Categorizer — `backend/expenses/categorizer.py`
```python
def categorize_expense(merchant: str, amount: float) -> str:
    # Returns: one of the CATEGORIES strings
```

#### CRUD — `backend/expenses/crud.py`
```python
def add_expense(expense: dict) -> dict:          # {success, id, message}
def update_expense(id: int, data: dict) -> dict  # {success, message}
def delete_expense(id: int) -> dict              # {success, message}
def get_all_expenses() -> list[dict]             # list of expense dicts
```

#### Analyzer — `backend/expenses/analyzer.py`
```python
def get_spending_summary() -> dict:
    # Returns: {total_spending, monthly_spending, by_category,
    #           monthly_trend, daily_spending, top_category, transaction_count}
```

#### AI Advisor — `backend/advisor/advisor.py`
```python
def generate_financial_advice(summary: dict, guru: str) -> dict:
    # Returns: {observation, recommendation, why, action, guru}
```

#### Budget Engine — `backend/budgeting/budget_engine.py`
```python
def get_budget_settings() -> dict         # {income, budgets: {cat: amount}}
def save_budget_settings(income, budgets) # {success, message}
def calculate_budget() -> dict            # full budget calculation result
```

#### Goals — `backend/budgeting/goals.py`
```python
def get_goals() -> list[dict]
def save_goal(goal: dict) -> dict
def update_goal(id: int, data: dict) -> dict
def delete_goal(id: int) -> dict
```

#### Splitwise — `backend/splitwise/splitwise_client.py`
```python
def get_splitwise_expenses() -> list[dict]:
    # Returns: [{group, description, total, user_share, date, paid_by}]
```

---

## Deploy to Streamlit Cloud

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial FinMate AI commit"
git remote add origin https://github.com/<your-username>/finmate-ai.git
git push -u origin main
```

Make sure `.gitignore` excludes `.env` and `__pycache__`:

```
.env
__pycache__/
*.pyc
*.pyo
venv/
.venv/
*.db
```

### Step 2 — Create Streamlit Cloud app

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository, branch `main`, and entry file `app.py`
5. Click **Deploy**

### Step 3 — Add secrets on Streamlit Cloud

In the app dashboard → **Settings** → **Secrets**, add:

```toml
OPENAI_API_KEY = "sk-..."
SPLITWISE_API_KEY = "..."
```

> The app works without these — it falls back to demo mode automatically.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | Powers the AI Advisor (Member 1) |
| `SPLITWISE_API_KEY` | No | Loads real Splitwise expenses |
| `SPLITWISE_CONSUMER_KEY` | No | Splitwise OAuth |
| `SPLITWISE_CONSUMER_SECRET` | No | Splitwise OAuth |
| `DATABASE_URL` | No | SQLite path (default: finmate.db) |

---

## Running Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
python -m pytest tests/ -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

Expected output:
```
tests/test_ui_helpers.py::TestExportUtils::test_export_expenses_csv_produces_bytes  PASSED
tests/test_ui_helpers.py::TestExportUtils::test_export_expenses_csv_header          PASSED
tests/test_ui_helpers.py::TestExportUtils::test_export_budget_csv                  PASSED
...
16 passed in Xs
```

---

## Member Responsibilities

| Area | Member |
|------|--------|
| Streamlit frontend, all pages, UI/UX, charts, export | **Member 2 (you)** |
| OCR engine, expense categorizer, SQLite database | Member 1 |
| AI advisor (OpenAI integration), spending analyzer | Member 1 |
| Budget calculation engine, goals database | Member 1 |
| Splitwise API integration, CSV parser | Member 1 |

---

## Mock / Demo Mode

The app runs **fully** without any backend modules. When Member 1's code is absent:

- Sample expenses (Swiggy, Uber, Amazon, Netflix…) are loaded automatically
- OCR returns a demo extraction with editable fields
- AI advisor shows template advice formatted per the selected guru
- All charts, budgets, and goals work with the sample data
- A yellow banner appears on each page indicating demo mode

To switch from mock to live, simply place Member 1's modules in the correct
`backend/` subdirectory. The adapter detects them on the next app reload — **no
frontend code changes required**.

---

## Privacy & Security

- No financial data is transmitted to external servers
- API keys are loaded from `.env` only — never hard-coded
- Uploaded screenshots are processed in memory and not persisted to disk
- All data is stored locally in SQLite (when backend is connected)

---

*FinMate AI · Track A · College Project · Built with ❤️ using Streamlit*
