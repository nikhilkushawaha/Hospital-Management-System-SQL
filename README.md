# Hospital Management System - SQL Project

A comprehensive SQL database project designed to manage and analyze hospital operations, including physician management, patient records, diagnoses, and medical procedures.

## 📋 Overview

Hospitals are critical institutions that provide essential medical facilities to people suffering from various illnesses. Managing day-to-day hospital activities and maintaining accurate records manually is challenging and error-prone. This project demonstrates how a relational database can streamline hospital operations, making data management more efficient and reliable.

The Hospital Database Management System (DBMS) is a comprehensive SQL project that provides an efficient solution for storing, retrieving, and manipulating healthcare-related data. It enables hospitals to manage physician schedules, patient diagnoses, medical histories, and other essential operations with ease.

## ✨ Features

- **Physician Management**: Track physicians, their positions, and department affiliations
- **Department Organization**: Manage multiple hospital departments with department heads
- **Patient Records**: Maintain comprehensive patient information including demographics and primary physicians
- **Diagnosis Tracking**: Record patient diagnoses and prescriptions
- **Medical Procedures**: Catalog medical procedures with associated costs
- **Nurse Management**: Track nursing staff and their registration status
- **Complex Queries**: Includes various SQL queries demonstrating data retrieval, joins, subqueries, and aggregations

## 🗄️ Database Schema

The database consists of **7 interconnected tables**:

### 1. **Physician**
Stores information about hospital physicians including employee ID, name, and position.

### 2. **Department**
Manages hospital departments with department ID, name, and department head (linked to Physician).

### 3. **Affiliated_with**
Junction table linking physicians to departments, indicating primary and secondary affiliations.

### 4. **Nurse**
Contains nurse information including ID, name, position, and registration status.

### 5. **Patient**
Stores patient demographics including ID, name, surname, address, gender, phone, and primary physician reference.

### 6. **Patient_Diagnosis**
Records patient diagnoses, prescriptions, and links them to both patients and treating physicians.

### 7. **Procedures**
Catalogs medical procedures with procedure codes, names, and associated costs.

## 🛠️ Technologies Used

- **Database**: MySQL
- **Language**: SQL
- **Analytics Layer**: Python (Pandas, SQLAlchemy, Matplotlib, Seaborn, Jupyter)

## 📁 Project Structure

```
hospitalManagementSQL/
├── Hospital_Database.sql          # Database schema and data insertion scripts
├── Hospital_Query.sql             # SQL queries for data analysis
├── HospitalDatabaseSchema.png     # Database schema visualization
├── README.md                      # Project documentation
│
└── python_analytics/              # ← Python analytics layer (NEW)
    ├── Hospital_Analytics.ipynb   #   Main notebook: connect → clean → analyze → visualize
    ├── config.py                  #   DATA_SOURCE toggle + DB credentials
    ├── data_loader.py             #   Load tables + build merged DataFrame
    ├── eda.py                     #   EDA, cleaning, normalization
    ├── insights.py                #   All analytical insight functions
    ├── visualizations.py          #   Matplotlib/Seaborn chart generation
    ├── export_to_csv.py           #   One-time MySQL → CSV exporter
    ├── requirements.txt           #   pip dependencies
    ├── data/                      #   Pre-exported CSVs (offline mode)
    └── visuals/                   #   Output PNG charts
```

## 🚀 Getting Started

### SQL Layer

**Prerequisites:** MySQL Server installed and running

1. **Clone or download this repository**

2. **Create the database and tables**:
   ```sql
   -- Run the Hospital_Database.sql file in your MySQL client
   -- This will create the database and all tables with sample data
   ```

3. **Execute queries**:
   ```sql
   -- Run queries from Hospital_Query.sql to explore the database
   ```

### 🐍 Python Analytics Layer

**No MySQL server required** — the notebook runs fully offline using pre-exported CSVs.

```bash
cd python_analytics
pip install -r requirements.txt
jupyter notebook Hospital_Analytics.ipynb
```

For live MySQL mode, update `MYSQL_CONFIG` in `config.py` and set `DATA_SOURCE = 'mysql'` in the notebook.  
See [`python_analytics/README.md`](python_analytics/README.md) for full setup instructions.

## 📊 Sample Queries

The project includes various SQL queries demonstrating:

- **Basic SELECT operations**: Filtering, sorting, and aggregations
- **JOIN operations**: Inner joins, left joins for relational data retrieval
- **Subqueries**: Nested queries for complex data analysis
- **String operations**: Pattern matching with LIKE operator
- **Data modifications**: UPDATE and ALTER TABLE operations
- **Statistical analysis**: Average costs, maximum values, etc.

Example queries include:
- Finding physicians by department
- Retrieving patient information with their primary physicians
- Calculating average procedure costs
- Filtering patients by diagnosis
- And many more...

## 🐍 Python Analytics Layer

The `/python_analytics` folder adds a complete data pipeline on top of the SQL database.

### What It Generates

| Analysis | Insight |
|---|---|
| Diagnosis frequency | Top diagnoses overall, by physician, by department |
| Physician workload | Diagnoses handled + primary care patients, ranked |
| Procedure cost analysis | Avg ₹2,628 · range ₹300–₹7,000 · distribution charts |
| Patient demographics | Gender split (Male/Female) + street-type geographic proxy |
| Data quality report | Null audit, duplicate detection, type validation |

### Charts Produced

| Chart | File |
|---|---|
| Top 10 Diagnoses (bar) | `visuals/top_diagnoses.png` |
| Physician Workload (grouped bar) | `visuals/physician_workload.png` |
| Procedure Cost Distribution (histogram + boxplot + catalog) | `visuals/procedure_cost_distribution.png` |
| Patient Gender Split (pie + bar) | `visuals/patient_gender_distribution.png` |
| Diagnoses by Department (bar) | `visuals/diagnoses_by_department.png` |

### Documented Schema Limitations

The pipeline explicitly flags what the current schema *cannot* support — a real-world data engineering practice:

- ❌ **Age distribution** — No `dob` field in `Patient`
- ❌ **Cost per patient** — No `patient_procedure` junction table
- ❌ **Geographic distribution** — Address is free-text, no city/state field

## 📈 Database Statistics

- **35 Physicians** across various specialties
- **15 Departments** covering major medical specialties
- **39 Patients** with complete demographic information
- **33 Nurses** with various positions and registration statuses
- **20 Medical Procedures** with associated costs
- **39 Diagnoses** covering a wide range of medical conditions

## 🔗 Table Relationships

- Physicians are linked to Departments through `Affiliated_with`
- Patients reference Physicians as their primary care provider
- Patient Diagnoses link Patients to Physicians
- Departments have Physicians as department heads

## 📝 Notes

- The database uses foreign key constraints to maintain referential integrity
- Sample data is provided for demonstration purposes
- All queries are documented with comments explaining their purpose
- The Python analytics layer is read-only — it never modifies the database

## 🤝 Contributing

This is a learning project demonstrating SQL database design and querying. Feel free to explore, modify, and extend the database structure and queries.

## 📄 License

This project is for educational purposes.

---

**Note**: This project demonstrates database design principles and SQL querying techniques for hospital management systems, extended with a Python data pipeline showcasing real-world analytics patterns (ETL, EDA, visualization, schema limitation documentation).
