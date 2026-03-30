# 🛒 Retail Transaction Insights Dashboard

A comprehensive, interactive data analytics dashboard built with **Python** and **Streamlit** for exploring retail transaction patterns, customer behaviour, promotional impact, and seasonal trends.

---

## 📌 Project Overview

This dashboard was developed as part of **Graded Mini Project: Part B — Retail Transaction Insights**. A nationwide retail chain's transaction dataset is analysed to uncover actionable insights that support strategic decision-making across customer segments, promotions, and seasonal performance.

---

## 🚀 Features

| Tab | Description |
|-----|-------------|
| 📊 **Overview** | Summary metrics, top products, and city-wise transaction counts |
| 👤 **Customer Behaviour** | Avg spend by category, payment preferences, items per store type |
| 🎁 **Promotions & Discounts** | Discount impact analysis, promotion effectiveness |
| 🌦️ **Seasonality** | Revenue by season, avg spending trends, store type preferences |
| 📈 **Dashboard** | City bar chart, payment pie chart, monthly revenue line, season heatmap |
| 💡 **Key Insights** | Auto-generated narrative insights derived from the data |

### Additional Capabilities
- **Sidebar Filters** - Filter all charts by Season, City, Customer Category, and Store Type interactively
- **K/M Abbreviations** - Large numbers displayed cleanly (e.g. $52.5M, 1000.0K)
- **Light Theme** - Clean, professional UI with custom styling

---

## 🗂️ Project Structure

```
W4_Project_Part_B/
├── retail_dashboard.py                  # Main Streamlit dashboard application
├── Retail_Transactions_Dataset.zip      # Dataset (compressed, auto-loaded on startup)
├── requirements.txt                     # Python dependencies
├── .gitignore                           # Excludes venv and uncompressed CSV
└── README.md                            # Project documentation
```

---

## 📦 Dataset

The dataset (`Retail_Transactions_Dataset.csv`) contains **1 million retail transaction records** with the following columns:

| Column | Description |
|--------|-------------|
| Transaction_ID | Unique identifier for each transaction |
| Date | Timestamp of the transaction |
| Customer_Name | Name of the customer |
| Product | List of items bought |
| Total_Items | Number of items purchased |
| Total_Cost | Total cost paid (USD) |
| Payment_Method | Mode of payment |
| City | City of the transaction |
| Store_Type | Type of store |
| Discount_Applied | Whether a discount was used |
| Customer_Category | Customer segment |
| Season | Season of the transaction |
| Promotion | Promotion type applied |

> ✅ The dataset (`Retail_Transactions_Dataset.zip`) is included in this repository.
> The dashboard will **automatically load it on startup** — no manual upload needed.

### Alternative — Manual Upload
A file uploader is available in the sidebar if you wish to load a different dataset:
- Upload via the sidebar in the running dashboard
---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- VS Code (recommended)

### Step 1 - Clone the repository
```bash
git clone https://github.com/rameshveluthedan-alt/AI-Lab.git
cd AI-Lab/W4_Project_Part_B
```

### Step 2 - Create and activate a virtual environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 3 - Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 - Run the dashboard
```bash
streamlit run retail-dashboard.py
```

### Step 5 - Upload the dataset
- The dashboard opens at `http://localhost:8501`
- Data loads **automatically** from the included zip file
- All charts and insights will populate automatically
- Optionally, upload a different CSV via the **sidebar uploader**

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core programming language |
| Streamlit | Web dashboard framework |
| Pandas | Data loading and manipulation |
| Plotly | Interactive charts and visualisations |
| Plotly Graph Objects | Heatmap and advanced charts |

---

## 📸 Dashboard Preview

| Section | Chart Types |
|---------|------------|
| Overview | Horizontal bar, vertical bar |
| Customer Behaviour | Grouped bar, stacked bar |
| Promotions | Bar charts, comparison charts |
| Seasonality | Line chart, grouped bar |
| Dashboard | Pie chart, heatmap, line chart |

---

## 👤 Author

**Ramesh Veluthedan** -AI Lab · Week 4 Project  
Course Assignment - Data Analytics with Python