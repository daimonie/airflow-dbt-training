
---
marp: true
theme: my-gaia
paginate: true
---

# Airflow + dbt Training Day (7h)  
## PDF Guide

---

## Overview  ad

This hands-on workshop introduces you to Airflow and dbt in a data engineering pipeline. By the end of the training, you will:

- Understand DAG design with dummy operators  
- Build PythonOperators calling reusable ingestion functions  
- Load weather and crime data into PostgreSQL  
- Use dbt to model this data into a data mart  
- Create and export a simple BI-style chart based on the output  

All development is done **inside the Airflow Docker container**, which includes:

- Airflow (LocalExecutor)  
- PostgreSQL (shared for Airflow metadata and dbt warehouse)

---

## Agenda

| Time        | Activity                                  |
|-------------|-------------------------------------------|
| 09:00–10:30 | Build basic ingestion DAGs (dummy + real) |
| 10:30–12:00 | Switch to real operators using data.py    |
| 12:00–13:00 | Lunch                                     |
| 13:00–15:00 | Set up dbt project + run staging models   |
| 15:00–16:15 | Combine models into mart + chart output   |
| 16:15–17:00 | Wrap-up, testing, and showing results     |

---

## Part 1: Basic Airflow DAG  
### (Dummy Operators)

You're setting up the skeleton of an Airflow DAG using dummy operators.

**For each DAG:**

- Create a Python file in `dags/`
- Use `with DAG(...) as dag:` structure
- Add `BashOperator` tasks
- Use `>>` for task ordering

---

## Part 1 Exercise

Make two DAGs:

- `ingest_weather` (daily)
- `ingest_crime` (weekly)

Each should have:

- `BashOperator` that echoes run ID  
- Placeholder `BashOperator` for ingestion

We'll replace these with real operators soon.

---

## Part 2: Data Ingestion  
### (Using `data.py`)

Replace dummy operators with real data ingestion steps.

**Each DAG:**

- Replace `BashOperator` with `PythonOperator`
- Use functions from `data.py`
- Chain with `>>`

---

## Helpers from `data.py`

```python
fetch_weather(city, endpoint) -> dict  
fetch_crime_data() -> pd.DataFrame  
load_data_into_database(df, table_name)  
read_data(filename) -> pd.DataFrame
```

Also:

```python
def read_data_into_database(filename):
    df = read_data(filename)
    load_data_into_database(df, "weather")
```

---

## PythonOperator Example

```python
from airflow.operators.python import PythonOperator

def ingest_sunny_weather():
    data = fetch_weather("Amsterdam", endpoint="sunny")
    load_data_into_database(data, "bronze.weather")

task = PythonOperator(
    task_id="ingest_sunny",
    python_callable=ingest_sunny_weather
)
```

---

## Part 2 Exercise

- Replace dummy operators with real ingestion  
- Use a list of endpoints and Jinja templating  
- Load into: `bronze.weather`, `bronze.crime`

---

## Part 3: dbt Setup and Usage

We're using **dbt Core**, not dbt Cloud — everything is CLI-driven.

You'll learn to:

- Set up reusable dbt projects  
- Structure data into bronze/staging/mart  
- Run models and tests using dbt operators  

---

## dbt Environment Setup

- Use `docker exec` or Docker Desktop to enter the Airflow container  
- Create `~/.dbt/profiles.yml` in `/opt/airflow/.dbt/`  
- Use the shared `airflow` PostgreSQL DB  
- Use `schemas` for bronze, staging, mart  

---

## dbt DAG Structure

Each DAG:

- Lives in a `.py` file  
- Uses `with DAG(...) as dag:`  
- Chains dbt operators with `>>`  

Available operators:

- `DbtCleanOperator`  
- `DbtDebugOperator`  
- `DbtRunOperator(select="tag:weather")`  
- `DbtRunOperator(select="tag:crime")`  
- `DbtRunOperator(select="exposure:weather_crime_mart")`  
- `DbtTestOperator(select="tag:mart")`

---

## dbt Exercise

Build a DAG that:

1. Cleans and debugs  
2. Runs weather + crime models  
3. Builds the mart  
4. Runs tests

Use dbt CLI inside container if needed:

```bash
dbt run --select tag:weather
```

---

## Part 4: Final Output  
### Create a Chart

Function available:

```python
create_chart(df, columns: List[str], filename: str)
```

Saves a seaborn chart using selected columns.

---

## Chart Exercise

- Query final mart table from PostgreSQL  
- Pass result to `create_chart`  
- Save output to `/tmp/chart.png`  

---

## Tips

- Use schemas: `bronze`, `staging`, `mart`  
- Keep dbt models small and focused  
- Use `ref()` in dbt instead of raw SQL joins  
- Restart Airflow if needed: `airflow standalone`

---

# Good luck!  
You're building your first real data pipeline.
