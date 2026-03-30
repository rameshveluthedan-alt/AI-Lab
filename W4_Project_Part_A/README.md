# 📚 Library Management System
> Academic project — Python 3.10+ · SQLite · Streamlit · Pandas

---

## 🚀 Quick Start

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
streamlit run lib_App.py
```

The browser will open at **http://localhost:8501**.  
The database file `library.db` is created automatically on first run.

---

## 🗂 Project Structure

```
library_ai_project/
│
├── lib_App.py                         # Streamlit UI — all pages & routing
│
├── db/
│   ├── __init__.py
│   ├── connection.py              # SQLite connection factory (FK ON)
│   ├── schema.py                  # DDL — creates tables on startup
│   └── crud.py                    # Parameterized SQL helpers (no raw strings)
│
├── services/
│   ├── __init__.py
│   ├── book_service.py            # Book business logic + validation
│   ├── member_service.py          # Member business logic + validation
│   ├── issue_service.py           # Atomic issue/return transactions
│   └── reporting_service.py      # Pandas-based analytics & reports
│
├── models.py                      # Dataclass entity definitions
├── requirements.txt
├── library.db                     # Auto-created SQLite database
└── README.md
```

---

## 🗄 Database Schema

### `books`
| Column | Type | Constraint |
|---|---|---|
| book_id | INTEGER | PK AUTOINCREMENT |
| title | TEXT | NOT NULL |
| author | TEXT | NOT NULL |
| category | TEXT | NOT NULL |
| isbn | TEXT | |
| published_year | INTEGER | |
| total_copies | INTEGER | CHECK ≥ 0 |
| available_copies | INTEGER | CHECK ≥ 0 |

### `members`
| Column | Type | Constraint |
|---|---|---|
| member_id | INTEGER | PK AUTOINCREMENT |
| name | TEXT | NOT NULL |
| gender | TEXT | CHECK IN ('Male','Female','Other') |
| age | INTEGER | CHECK > 0 |
| mobile_number | TEXT | |
| email | TEXT | NOT NULL, UNIQUE |
| join_date | TEXT | DEFAULT current date |

### `transactions`
| Column | Type | Constraint |
|---|---|---|
| transaction_id | INTEGER | PK AUTOINCREMENT |
| book_id | INTEGER | FK → books |
| member_id | INTEGER | FK → members |
| issue_date | TEXT | DEFAULT today |
| return_date | TEXT | nullable |
| status | TEXT | CHECK IN ('Issued','Returned') |

---

## ✅ Features

| Feature | Details |
|---|---|
| Book CRUD | Add / update / delete / search by title, author, category |
| Member CRUD | Add / update / delete / search with email uniqueness |
| Issue Book | Atomic: decrement copies + create transaction |
| Return Book | Atomic: increment copies + update transaction |
| Safety guards | Cannot delete book or member with active issues |
| Reports | Issued, Overdue, Most Borrowed, Member History, Inventory |
| CSV Export | All report tables are downloadable |
| Dashboard | Live stats + top borrowed + overdue snapshot |
| Logging | Python `logging` module throughout service layer |

---

## 🧠 AI-Ready Design

The architecture is intentionally structured for future ML/AI extensions:

```
services/
  └── reporting_service.py   ← Returns clean Pandas DataFrames
                               → Feed directly into sklearn, PyTorch, etc.

models.py                    ← Dataclasses map cleanly to feature vectors

Future modules you can add:
  services/recommendation_service.py   # Collaborative filtering
  services/overdue_predictor.py        # Logistic regression on borrowing patterns
  services/demand_forecaster.py        # Time-series on utilisation_pct
```

Key extensibility points:
- `report_most_borrowed_books()` → input for item-based recommendation
- `report_member_borrowing_history()` → user-item matrix for collaborative filtering
- `report_inventory()` → `utilisation_pct` column → demand forecasting signal
- `report_overdue_books()` → label column for supervised overdue prediction

---

## 🔒 Security Notes

- All SQL uses **parameterized queries** — no string interpolation, no SQL injection risk
- Email is validated via regex before any DB write
- `PRAGMA foreign_keys = ON` enforced on every connection
- `CHECK` constraints enforced at DB level as a second layer

---

## 🖥 UI Navigation

| Page | Purpose |
|---|---|
| 🏠 Dashboard | KPI cards, top books, overdue snapshot |
| 📚 Books | View/search, add, update, delete books |
| 👥 Members | View/search, register, update, delete members |
| 🔄 Issue/Return | Issue books to members, process returns, view active |
| 📊 Reports | 5 detailed reports with CSV export and charts |
