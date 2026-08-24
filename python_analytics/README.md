# 🐍 Hospital Analytics — Python Data Pipeline

A Python-based analytics layer built on top of the [Hospital Management System SQL](../README.md) project. Demonstrates a real-world data pipeline pattern: connect to a relational database → load into Pandas → clean → analyze → visualize.

---

## 🎯 What This Demonstrates

| Skill | How |
|---|---|
| **Database connectivity** | SQLAlchemy engine with dual MySQL / CSV mode |
| **ETL / Data Loading** | Multi-table joins across 5 related tables into a master DataFrame |
| **EDA & Data Quality** | Null audits, duplicate detection, type validation, normalization |
| **Analytical Insights** | Groupby, aggregation, ranking, value counts |
| **Data Visualization** | Matplotlib + Seaborn: bar charts, histograms, boxplots, pie charts |
| **Portfolio Best Practice** | Offline-runnable (CSV mode), modular codebase, documented schema limitations |

---

## 📁 Structure

```
python_analytics/
├── Hospital_Analytics.ipynb   ← Main notebook (run this)
├── config.py                  ← DATA_SOURCE toggle + DB credentials
├── data_loader.py             ← Load raw tables + build merged DataFrame
├── eda.py                     ← EDA, cleaning, normalization
├── insights.py                ← All analysis functions
├── visualizations.py          ← All chart functions (saves PNGs)
├── export_to_csv.py           ← One-time MySQL → CSV exporter
├── requirements.txt           ← pip dependencies
│
├── data/                      ← Pre-exported CSVs (offline mode)
│   ├── physician.csv
│   ├── department.csv
│   ├── affiliated_with.csv
│   ├── nurse.csv
│   ├── patient.csv
│   ├── patient_diagnosis.csv
│   └── procedures.csv
│
└── visuals/                   ← Output PNG charts (auto-created)
    ├── top_diagnoses.png
    ├── physician_workload.png
    ├── procedure_cost_distribution.png
    ├── patient_gender_distribution.png
    └── diagnoses_by_department.png
```

---

## 🚀 Quick Start (No MySQL Required)

```bash
# 1. Navigate into this directory
cd python_analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the notebook
jupyter notebook Hospital_Analytics.ipynb
```

The notebook defaults to `DATA_SOURCE = "csv"` — all data is pre-loaded from `/data/`, no MySQL server needed.

---

## 🗄️ Live MySQL Mode

1. Make sure your MySQL server is running and the `HOSPITAL_MANAGMENT_SYSTEM` database exists  
   (run `Hospital_Database.sql` from the root if not)

2. Update credentials in `config.py`:
   ```python
   MYSQL_CONFIG = {
       "host": "localhost",
       "port": 3306,
       "user": "root",
       "password": "your_password",
       "database": "HOSPITAL_MANAGMENT_SYSTEM",
   }
   ```

3. In the notebook's **Section 1**, change:
   ```python
   config.DATA_SOURCE = 'mysql'
   ```

4. Or export the live DB to CSV once and switch back to CSV mode:
   ```bash
   python export_to_csv.py
   ```

---

## 📊 Insights Generated

### 1. Diagnosis Frequency
- Top 10 most common diagnoses across all patients
- Breakdown by physician
- Breakdown by department (via primary affiliation)

### 2. Physician Workload
- Diagnoses handled per physician (ranked)
- Patients under primary care per physician
- Combined workload comparison

### 3. Procedure Costs
- Average, median, min, max, std dev of catalog prices
- Ranked cost catalog (all 20 procedures)
- Distribution visualized as histogram + boxplot

### 4. Patient Demographics
- Gender distribution (Male / Female split)
- Address street-type distribution (geographic proxy)
- Nurse registration breakdown by position

---

## ⚠️ Known Schema Limitations

These insights were requested but **cannot be computed** from the existing schema:

| Insight | Reason | Schema Fix |
|---|---|---|
| Age distribution | No `dob` or `age` field in `Patient` | `ALTER TABLE Patient ADD COLUMN dob DATE` |
| Cost per patient / department | No `patient_procedure` junction table | `CREATE TABLE patient_procedure (patient_id, procedure_code, date)` |
| Real geographic distribution | `address` is free-text street strings — no city/state/ZIP | Add `city VARCHAR(100)`, `state VARCHAR(50)` to `Patient` |

These limitations are documented in **Section 8** of the notebook and are visible as a learning artifact: good data engineering includes flagging what the data *can't* support.

---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---|---|---|
| `pandas` | ≥ 2.0 | DataFrames, joins, aggregations |
| `sqlalchemy` | ≥ 2.0 | DB engine (MySQL / SQLite) |
| `mysql-connector-python` | ≥ 8.0 | MySQL driver for SQLAlchemy |
| `matplotlib` | ≥ 3.7 | Chart rendering |
| `seaborn` | ≥ 0.12 | Statistical visualization layer |
| `jupyter` | ≥ 1.0 | Notebook environment |

---

## 🔗 Relationship to SQL Project

This pipeline is **read-only** — it never writes to or modifies the MySQL database. It reads the same 7 tables defined in `Hospital_Database.sql` and adds a Python analytics layer on top, without disrupting the original SQL-only project.
