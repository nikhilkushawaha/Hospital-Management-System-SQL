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

## 📁 Project Structure

```
hospitalManagementSQL/
├── Hospital_Database.sql      # Database schema and data insertion scripts
├── Hospital_Query.sql         # SQL queries for data analysis
├── HospitalDatabaseSchema.png # Database schema visualization
├── Hospital Management System Questions.pdf
├── HOSPITAL MANAGEMENT SYSTEM.pdf
└── README.md                  # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- MySQL Server installed and running
- MySQL Workbench or any MySQL client (optional, for GUI)

### Installation

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

### Database Setup

Execute the following in your MySQL client:

```sql
-- The Hospital_Database.sql file contains:
-- 1. Database creation
-- 2. Table creation with proper relationships
-- 3. Sample data insertion
-- 4. Basic SELECT statements for verification
```

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

## 📈 Database Statistics

- **35 Physicians** across various specialties
- **15 Departments** covering major medical specialties
- **39 Patients** with complete demographic information
- **33 Nurses** with various positions and registration statuses
- **20 Medical Procedures** with associated costs
- **Multiple Diagnoses** covering a wide range of medical conditions

## 🔗 Table Relationships

- Physicians are linked to Departments through `Affiliated_with`
- Patients reference Physicians as their primary care provider
- Patient Diagnoses link Patients to Physicians
- Departments have Physicians as department heads

## 📝 Notes

- The database uses foreign key constraints to maintain referential integrity
- Sample data is provided for demonstration purposes
- All queries are documented with comments explaining their purpose

## 🤝 Contributing

This is a learning project demonstrating SQL database design and querying. Feel free to explore, modify, and extend the database structure and queries.

## 📄 License

This project is for educational purposes.

---

**Note**: This project demonstrates database design principles and SQL querying techniques for hospital management systems. It can serve as a foundation for more complex healthcare management applications.
