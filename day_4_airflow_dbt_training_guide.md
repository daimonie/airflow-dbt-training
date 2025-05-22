# Airflow + dbt Training Day (7h) - PDF Guide

---

### Overview

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

### Agenda

| Time        | Activity                                  |
|-------------|-------------------------------------------|
| 09:00–10:30 | Build basic ingestion DAGs (dummy + real) |
| 10:30–12:00 | Switch to real operators using data.py    |
| 12:00–13:00 | Lunch                                     |
| 13:00–15:00 | Set up dbt project + run staging models   |
| 15:00–16:15 | Combine models into mart + chart output   |
| 16:15–17:00 | Wrap-up, testing, and showing results     |

---

### Part 1: Basic Airflow DAG (Dummy Operators)

We're starting simple: you're setting up the skeleton of an Airflow DAG using operators that just print something out. These are stand-ins — scaffolding we'll replace soon.

For each DAG:

- Create a new Python file in the `dags/` folder — one file per DAG.
- Use the structure `with DAG(dag_id, schedule, description) as dag:` to define the DAG body.
- For each step in your workflow, add a task. That just means assigning a `BashOperator` (or later, a `PythonOperator`) to a variable.
- Finally, wire your steps together using `>>` (task ordering).

**Your exercise:**

- Make two DAGs:
  - `ingest_weather`: daily schedule
  - `ingest_crime`: weekly schedule
- Each should have:
  - a `BashOperator` that echoes the run ID
  - another `BashOperator` placeholder for where our data ingestion will go

We'll make these real soon — for now, this is about getting structure in place.

---

### Part 2: Data Ingestion (Using `data.py`)

Now we’ll plug in actual functionality: fetching weather and crime data, and loading it into the database.

**For each DAG:**

- Stick to the same structure: one file per DAG, `with DAG(...) as dag:`
- Replace the second `BashOperator` from before with a `PythonOperator`
- Use a clear task name, and call the functions from `data.py`
- Chain your tasks using `>>` to define the run order

**Available helpers in `data.py`:**

```python
fetch_weather(city, endpoint) -> dict
fetch_crime_data() -> pd.DataFrame
load_data_into_database(df, table_name)
read_data(filename) -> pd.DataFrame
```

You can also use:

```python
def read_data_into_database(filename):
    df = read_data(filename)
    load_data_into_database(df, "weather")
```

We’ll also "realize" (spoiler alert: you will be told) that there are multiple endpoints for weather data (e.g. current, hourly, daily), so you'll use a Jinja loop to fetch them in a clean way.

**Your exercise:**

- Replace dummy operators with `PythonOperator`s that actually ingest data
- To use a `PythonOperator`, you'll need to wrap the function you want to call in another function with no arguments (Airflow will pass context via kwargs if needed). For example:

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

- Use a list of endpoints and Jinja templating to loop over weather calls
- Load into PostgreSQL: `bronze.weather`, `bronze.crime`

---

### Part 3: dbt Setup and Usage

Before we dive in — a quick reminder: we're using **dbt Core**, running locally inside the container. That means no dbt Cloud features, no UI, no lineage explorer — just the CLI and static docs. Everything is still powerful, just less fancy.

This is also where we make things useful for your real-world projects. We'll show how you can turn your setup into **reusable templates** — the same structure you're building today can be adapted to other APIs, different database tables, or new dashboards in your own workplace.

We’ll start by reconnecting the dots between bronze/silver/gold layers and what you might know as landing/enriched/curated. The idea is simple: treat your raw data like an inbox, transform it into something clean, and then prepare it for actual use.

Before doing anything fancy, we’ll configure dbt inside the same container you’re running Airflow in. You can use **Docker Desktop** to open a terminal in the running Airflow container, or use `docker exec -it <container_id> bash` to enter it manually.

Once you're in, you'll need to make sure the `profiles.yml` file exists at `/opt/airflow/.dbt/profiles.yml`. This is the default location that dbt uses in this environment — placing it here allows both dbt and Airflow to access the same configuration.

Use `mkdir -p /opt/airflow/.dbt` to create the folder if it doesn't exist, and then edit the file with `nano`, `vim`, or by mounting a volume if you're more comfortable editing locally.

- Connect to the same PostgreSQL database (`airflow`)
- Use schemas like `staging` and `mart` to separate model layers

**Each DAG here should:**

- Live in its own `.py` file
- Use `with DAG(...) as dag:`
- Add steps using the custom dbt operators below
- Chain them together using `>>`

**dbt Operators available to you:**

- `DbtCleanOperator`
- `DbtDebugOperator`
- `DbtRunOperator(select="tag:weather")`
- `DbtRunOperator(select="tag:crime")`
- `DbtRunOperator(select="exposure:weather_crime_mart")`
- `DbtTestOperator(select="tag:mart")`

**Your exercise:**

- Set up a DAG that runs:
  - clean + debug
  - then builds weather + crime tagged models
  - then builds the mart
  - and finally runs tests

**Note**: `dbt docs generate` will still work — it produces an HTML file with the DAG and metadata — but there's no fancy UI here. Just static files.

---

### Part 4: Final Output — Create a Chart

Function available:

```python
create_chart(df, columns: List[str], filename: str)
# Saves a seaborn chart using selected columns
```

**Exercise:**

- Query the final mart table from PostgreSQL
- Pass result to `create_chart`
- Save a line or bar chart to `/tmp/chart.png`

---

### Tips

- Use one schema per stage: `bronze`, `staging`, `mart`
- Keep models small and focused — use `ref()` instead of joins in raw SQL
- You can run `dbt run` manually inside the container too:

```bash
dbt run --select tag:weather
```

- Restart Airflow with `airflow standalone` if needed inside the container

---

**Good luck! You're building your first real data pipeline.**
