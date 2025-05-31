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

# Start up
Before we continue, start our images. We'll need a little bit extra this time:
```
git pull
docker-compose build
docker-compose down
docker-compose up -d
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
    file_path=file_path,
    xcom_task_id='process_table'
)

```

---

# Exploring Your Data Warehouse

Built-in tools to explore loaded data:

```python

    # List all tables in the data warehouse
    list_tables = ListDWHTables(
        task_id='list_dwh_tables',
        connection_id='dwh',
        schema='public'
    )

    # Describe specific EP 1989 table
    describe_ep_1989 = DescribeDWHTable(
        task_id='describe_ep_1989',
        connection_id='dwh',
        table_name='europees_parlement_landelijk__1989_4280',
        schema='public'
    )

```

---

# Morning plan

Two tasks.
1. Select the data you want to use for modelling. This might be a group activity.
2. Create the import DAG using the tools from the past slides / handout!

The DAG should look something like this:
```
process_police_table_table_one >> upload_police_table_table_one
process_police_table_table_two >> upload_police_table_table_two
process_police_table_table_three >> upload_police_table_table_three
```
Let's make sure to produce *Assets*. For postgres, they look like this:
```
Asset("postgres://host:port/database/schema/table")
```
**NB**: *Dataset* is the old name of *Asset* in airflow. In case you run into that.

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

# DBT Models
DBT lets you write SQL files (Transformations) and add context using either `schema.yml` or a `config` block in jinja.

Models refer to each other by either using `ref` (another model) or `source` (a source loaded via something else):
```
SELECT * FROM FROM {{ source('public', 'raw_housing_prices') }} 
```
or
```
SELECT *  FROM {{ ref('stg_housing_prices') }} 
```

---

# DBT Commands

We familiarized ourselves with a long list of commands:
- dbt debug
- dbt run
- dbt compile
- dbt build
- dbt test

And with selecting our `tags` or other patterns via `--select tag:bronze`. And we wrote macros, re-useable functions or pieces of SQL.

---


# Setting Up dbt

Normally, you create a new dbt project:

```bash
# Initialize new project
dbt init police_analytics

```
But in our case, we have our sandbox project from last week. Let's re-use it.

---

# dbt Profiles Generator

First, let's reuse our connection and make sure dbt is configured to use it:
```
  # Create dbt profiles from Airflow connection
  generate_profiles = DbtGenerateProfilesOperator(
      task_id='generate_dbt_profiles',
      connection_id='dwh',  # Use the same connection as UploadToDWHOperator
  )
```

---

# dbt debug

Let's see if the connection works.
```

    # Run dbt debug to verify configuration
    dbt_debug = DbtDebugOperator(
        task_id='dbt_debug',
        config=True  # Added config flag to show all configuration info
    )
```

---

# Alright, let's run everything? Generally, you'll want to split this so that it is clear what works and what doesn't.

```
    # Run dbt models
    dbt_run = DbtRunOperator(
        task_id='dbt_run'
    )
```

---

# dbt Test
And finally, let's see if the data and modelled data follows our tests:

```
    # Run dbt tests
    dbt_test = DbtTestOperator(
        task_id='dbt_test',
        select='+tag:silver'
    )

    dbt_run >> dbt_test\
```
If we split this by zoning, we can see whether it is raw data, enriched data or marts that don't test well

---

# Afternoon plan

This morning, we loaded tables and defined them as assets:

```
Asset("postgres://host:port/database/schema/table")
```
We'll use the defined assets to let Airflow know **when to trigger dbt workflows**. The plan:

1. Model the assets you wanted to model
2. Ideally we have 1-2 `exposures` that we want to use.
2. Setup the airflow DAG to run DBT in modular chunks - bronze/silver/gold is fine, but running per exposure is also great!

*NB*: I added tags to all the models, so at the moment you can see how we used the `schema.yml` to set tags for bronze, silver and gold.

---

## Wrap-Up: From Data to Models

Today you learned to:

✅ Discover and select real-world open datasets  
✅ Build custom Airflow DAGs to ingest data  
✅ Upload structured data to a data warehouse  
✅ Define dbt models and run them on trigger  
✅ Use tags and assets to organize your workflow

Next steps? Add documentation, tests, exposures — and make it shine.

---

# Unlimited Assets

![Unlimited Assets](/home/marp/app/unlimited_assets.jpeg)

---

# Assets: A Word of Warning

Assets are a fairly new feature in Airflow. While powerful, they can impact scheduler performance.

A better strategy is:
- Load raw tables without Assets
- Create one Asset at the end of your pipeline
- Use that Asset to trigger downstream DAGs

This gives you:
- Better scheduler performance
- Cleaner metadata database
- Still have DAG-to-DAG dependencies

Think of Assets as checkpoints, not individual files!
