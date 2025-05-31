---
marp: true
theme: gaia
paginate: true
---

<style>
:root {
  --color-background: #ffffff;     /* pure white */
  --color-foreground: #1f331f;     /* deep green-black for main text */
  --color-highlight: #228b22;      /* ForestGreen for links and accents */
  --color-dimmed: #6b8f6b;         /* muted desaturated ForestGreen */
  --color-table-header: #1a5e1a;   /* strong dark green for tables */
  --color-table-header-text: #ffffff; /* white text on dark green */
}

section {
  font-size: 24px;  /* Base font size for slides */
}

h1 {
  font-size: 1.6em;  /* Relative to section font size */
}

h2 {
  font-size: 1.3em;  /* Relative to section font size */
}

/* Optional: style table headers if using standard Markdown tables */
table th {
  background-color: var(--color-table-header);
  color: var(--color-table-header-text);
  font-weight: bold;
  padding: 0.4em 0.6em;
  border-bottom: 2px solid #cccccc;
}

table td {
  padding: 0.4em 0.6em;
  border-bottom: 1px solid #eeeeee;
}
</style>

<!-- _class: lead -->

# Day 4: From Data to Insights
## Working with Police Open Data & Data Modeling

---

# Morning Agenda
0. Recap
1. Exploring Police Data Sources
2. Loading Data into Our Warehouse
3. Setting Up Automated Data Pipelines

---

# Airflow Recap

Airflow is a scheduling tool where you write workflows in Python.  The basic concepts:
- A **DAG** is a Direct Acrylic Graph - a directed flowchart without loops
- A **Task** is, well, a task in your workflow.
- An **Asset** is a way of telling Airflow that you want to write a file/dataset/table and want downstream DAGs to trigger off that update

---

# Tasks

Tasks are the re-useable units in an airflow workflow. We familiarised ourselves with some:
- **BashOperator**: A simple task to run a Bash command (linux command)
- **PythonOperator**: A task to run a python function
- The **@task** decorator: A shorter way of turning your python function into a task
- The **@task.branch decorator**: A way of inserting what/if logic into your task, deciding which branch of the DAG will be executed

I've made a few new Operators you can use today.

---

# XCom

Cross-commmunication: How do tasks talk to each other?

This can be done more manually, but we will use the pythonic way:
```
task_with_output = SomeTaskOperator(task_id="task_with_output")
task_with_input = SomeOtherTaskOperator(task_id="task_with_input", input=task_with_output)

task_with_output >> task_with_input
```
Or, if using decorators:
```
task_with_output = some_task()
task_with_output >> task_with_input(task_with_output)
```

---

# Police Data Explorer

I've created some custom Airflow operators to help you explore police-related data.

The first will search in the open dataset (CBS+Police) for tables that mention the `search_term`.
You can also do this on the police website at `https://data.politie.nl/#/Politie/nl/`.

The List operator: Run it, and check the logs to find out what you found!

```python
# List all police-related tables
list_tables = ListPoliceTables(
    task_id='list_police_tables',
    search_term='politie'  # Can use other search terms too!
)
```

This will find all CBS Open Data tables related to police/law enforcement.

---

# Processing Police Data

Once you find interesting tables, you can process them:

```python
# Process a single table
process_table = ProcessPoliceTable(
    task_id='process_budget',
    table_name='police_budget_2023'
)

```

---

# Loading Data to the Warehouse

After processing, load data to your warehouse:

```python
# Upload processed data
upload = UploadToDWHOperator(
    task_id='upload_to_dwh',
    connection_id='dwh',
    xcom_task_id='process_table'
)

```

---

# Exploring Your Data Warehouse

Built-in tools to explore loaded data:

```python
# List all tables
list_dwh = ListDWHTables(
    task_id='list_tables',
    connection_id='dwh',
    schema='public'
)

# Describe a specific table
describe = DescribeDWHTable(
    task_id='describe_table',
    connection_id='dwh',
    table_name='police_budget_2023'
)
```

---

# Nuclear Option 🚀

If time is short, we have a pre-configured pipeline that can:
- Load ALL police-related tables
- Process them automatically
- Load them into your warehouse

Just let us know if you need this option!

---

# Afternoon Preview

After lunch, we'll:
1. Set up a dbt project
2. Create data models
3. Build transformations
4. Add exposure metadata
5. Connect to visualization tools

# Afternoon Agenda

1. Recap
2. Setting Up Your Project
3. Creating Data Models
4. Testing & Documentation
5. Creating Exposures

---

# Reminder: What is dbt?

dbt (data build tool) helps you:
- Transform data in your warehouse
- Version control your transformations
- Test your data quality
- Document your data models
- Track data lineage

---

# Setting Up dbt

Create a new dbt project:

```bash
# Initialize new project
dbt init police_analytics

# Directory structure
police_analytics/
  models/           # Your SQL transformations
  tests/            # Custom data tests
  macros/          # Reusable SQL snippets
  seeds/           # Static data files
  dbt_project.yml  # Project configuration
```

---

# Configuring Your Project

Edit `dbt_project.yml`:

```yaml
name: 'police_analytics'
version: '1.0.0'

profile: 'default'  # Uses same warehouse connection

models:
  police_analytics:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

---

# Creating Your First Models

Start with staging models (`models/staging/`):

```sql
-- models/staging/stg_police_budget.sql
SELECT
    year,
    department,
    CAST(budget_amount AS DECIMAL) as budget_amount,
    currency
FROM {{ source('raw', 'police_budget_2023') }}
```

---

# Building Marts

Create business-level models (`models/marts/`):

```sql
-- models/marts/department_spending.sql
SELECT
    department,
    SUM(budget_amount) as total_budget,
    COUNT(DISTINCT year) as years_of_data
FROM {{ ref('stg_police_budget') }}
GROUP BY department
```

---

# Testing Your Models

Add tests in `schema.yml`:

```yaml
version: 2

models:
  - name: stg_police_budget
    columns:
      - name: budget_amount
        tests:
          - not_null
          - positive_values

  - name: department_spending
    columns:
      - name: department
        tests:
          - unique
          - not_null
```

---

# Adding Documentation

Document your models in `schema.yml`:

```yaml
version: 2

models:
  - name: department_spending
    description: >
      Aggregated view of department-level police spending
      across all available years.
    columns:
      - name: department
        description: Police department name/identifier
      - name: total_budget
        description: Total budget allocated across all years
```

---

# Creating Exposures

Define how your data is used:

```yaml
version: 2

exposures:
  - name: police_budget_dashboard
    type: dashboard
    maturity: high
    url: https://your-bi-tool/dashboards/police-budget
    description: >
      Executive dashboard showing police budget allocation
      and spending patterns across departments.
    depends_on:
      - ref('department_spending')
    owner:
        name: Analytics Team
        email: analytics@police.gov
```

---

# Running dbt

Essential commands:

```bash
# Build all models
dbt run

# Run all tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Build specific models
dbt run --select marts.department_spending+
```

---

# Best Practices

1. Use staging models for cleaning/standardization
2. Build marts for business concepts
3. Test critical assumptions
4. Document as you go
5. Use exposures to track usage
6. Follow consistent naming conventions

---

# Putting It All Together

Your final project should have:
- Clean, staged source data
- Transformed business-level models
- Comprehensive tests
- Clear documentation
- Defined exposures

Questions? Let's start building! 🚀