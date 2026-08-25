# Retail Sales Lakehouse

Production-style end-to-end Data Engineering project for retail analytics.

The platform transforms messy retail source data into validated, analytics-ready datasets and exposes business insights through Power BI.

## Architecture

```text
Source Data
    |
    v
Python Ingestion
    |
    v
Bronze - Parquet
    |
    v
Data Quality Validation
    |
    v
Silver - Parquet
    |
    v
dbt Transformations
    |
    v
Gold - PostgreSQL
    |
    v
Power BI

Apache Airflow orchestrates the pipeline.

Technology Stack
Python
Pandas
PostgreSQL
Apache Airflow
dbt
Great Expectations
Docker
Parquet
SQL
Power BI
Git / GitHub
Current Status
Milestone 1
 Repository initialized
 Docker environment created
 PostgreSQL configured
 Airflow configured
 Airflow health-check DAG created
 

Project Goal

Build a reliable retail analytics platform that enables business stakeholders to understand sales, profitability, customer, product, regional, and operational performance.

Local Setup
Clone the repository.
Create a .env file from .env.example.
Start the Airflow initialization container.
Start the Docker Compose environment.
Open Airflow at http://localhost:8080.
Credentials

Local development credentials are stored in .env.

Do not commit .env to Git.

License

MIT