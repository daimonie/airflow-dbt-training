---

marp: true
paginate: true
headingDivider: 2
-----------------

# Day 3 – Advanced dbt Concepts (Local + Cloud)

---

## Welcome Back! 🚀

* What we built yesterday:

  * Bronze → Silver → Gold
  * Schema tests and documentation
  * dbt docs and lineage
* What you’ll learn today:

  * Smarter ways to model
  * How to re-use logic in dbt
  * Advanced tests and exposures
  * Preview of dbt Cloud

---

## Agenda – Day 3

1. Incremental models
2. Re-using logic with macros
3. Custom tests and ownership with exposures
4. Guided project extension
5. Intro to dbt Cloud

---

## Recap & Q\&A

* What went well yesterday?
* Any issues with:

  * Running models or tests?
  * Model structure or naming?
  * Docs or lineage visibility?

---

## Incremental Models – Why?

* Large models don’t need to reprocess everything every time
* dbt lets you process **only new or changed rows**
* This can save time and money in production

---

## Incremental Models – Logic Pattern

```sql
{{ config(materialized='incremental', unique_key='id') }}

SELECT *
FROM {{ source('public', 'raw_housing_prices') }}
{% if is_incremental() %}
  WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

---

## Hands-On: Create an Incremental Model (Part 1)

### Step 1: Open the dbt container

* Open **Docker Desktop**
* Go to **Containers / Apps**
* Click the `dbt` container
* Open a **terminal** in that container

---

## Hands-On: Create an Incremental Model (Part 2)

### Step 2: Create a new model file

In the terminal, type:

```bash
nano models/silver/incremental_prices.sql
```

Paste:

```sql
{{ config(materialized='incremental', unique_key='id') }}

SELECT *
FROM {{ ref('housing_prices') }}
{% if is_incremental() %}
  WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Understanding the Config Block

At the top of the model file, we used this line:

```jinja
{{ config(materialized='incremental', unique_key='id') }}
```

Here's what it means:

* `materialized='incremental'` tells dbt to treat this model as **incremental** — it only adds or updates new data after the first run.
* `unique_key='id'` tells dbt how to match rows — needed to avoid duplicates.

This line uses **Jinja**, the templating language used in dbt. dbt uses Jinja to let you insert logic or configuration into SQL files before running them. Even though you're writing `.sql` files, everything inside `{{ }}` or `{% %}` is interpreted by dbt first, not directly by the database.

---

## Run the Incremental Model (Part 1)

### Step 1: Run the model

In the same terminal:

```bash
dbt run --select incremental_prices
```

Check that it says `materialized: incremental`

---

## Run the Incremental Model (Part 2)

### Step 2: Run it again to test the logic

We’ll now see if dbt *skips* rows it already handled.

### Check row count before:

Open **Docker Desktop**, go to **Containers → dwh**, click **Terminal**, and type:

```bash
psql -U postgres -d dwh
```

Then inside psql:

```sql
SELECT COUNT(*) FROM silver.incremental_prices;
```

---

## Simulate Updated Data (Part 1)

To simulate new data, we’ll update 10 rows in the **source table**.

### Step 1: Open the `dwh` container

* Open **Docker Desktop**
* Go to **Containers → dwh**
* Click **Terminal**, then type:

```bash
psql -U postgres -d dwh
```

---

## Simulate Updated Data (Part 2)

### Step 2: Run this SQL command:

```sql
UPDATE public.raw_housing_prices
SET updated_at = NOW()
WHERE id IN (
  SELECT id FROM public.raw_housing_prices
  ORDER BY RANDOM()
  LIMIT 10
);
```

This will change the `updated_at` field for 10 random rows.

Now, we’ll rerun the model to pick up those changes.

---

## Rerun the Model (Part 1)

Now rerun the model to test incremental behavior:

In the **dbt container terminal**, type:

```bash
dbt run --select incremental_prices
```

* This should complete quickly if nothing has changed.
* You should see `0 rows affected` if no new rows were added.

---

## Rerun the Model (Part 2)

### Check the row count again:

Return to the `dwh` container:

```bash
psql -U postgres -d dwh
```

Then run:

```sql
SELECT COUNT(*) FROM silver.incremental_prices;
```

Only new rows should be added — not duplicates.

* In the same terminal, type:

```bash
dbt run --select incremental_prices
```

* Confirm it shows as `incremental`
* Run it **again** to confirm it only adds new data

---

## Add a Test: No Duplicate IDs

Open the schema file:

```bash
nano models/silver/schema.yml
```

Add this under `models:`:

```yaml
  - name: incremental_prices
    columns:
      - name: id
        tests:
          - unique
```

Save and run:

```bash
dbt test --select incremental_prices
```

---

## Repetition: Why Reuse Logic?

You now have a powerful pattern: models that are efficient and tested.

But there’s a new challenge:

* We often copy the **same logic** (like `CASE` statements or filters) across models.
* When the logic changes, we’d have to update it in **many files**.

We want to:

* Write the logic once
* Use it in multiple places
* Make updates easier and safer

In dbt, we do this using a tool called a **macro**.

* We often write the **same CASE or filters** in multiple models
* When the logic changes, we want to change it **once**
* In dbt, we reuse logic by creating a **macro**

---

## Macros – Example

Create a macro to normalize type:

```jinja
{% macro normalize_type(column_name) %}
  CASE
    WHEN LOWER({{ column_name }}) = 'urban' THEN 'URBAN'
    WHEN LOWER({{ column_name }}) = 'rural' THEN 'RURAL'
    ELSE 'UNKNOWN'
  END
{% endmacro %}
```

Use it in a model:

```sql
SELECT {{ normalize_type('type') }} as type_cleaned
```

---

## Hands-On: Write and Use a Macro

### Step 1: Open the dbt container

(If it’s closed, repeat the Docker Desktop steps)

### Step 2: Open the macros folder

```bash
nano macros/normalize_type.sql
```

Write the macro yourself (no copy-paste):

```jinja
{% macro normalize_type(column_name) %}
  CASE
    WHEN LOWER({{ column_name }}) = 'urban' THEN 'URBAN'
    WHEN LOWER({{ column_name }}) = 'rural' THEN 'RURAL'
    ELSE 'UNKNOWN'
  END
{% endmacro %}
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 3: Use the macro

Open a silver model and use:

```sql
SELECT {{ normalize_type('type') }} AS cleaned_type
```

Run the model and inspect the results.

---

## Custom Tests in dbt

* A **custom test** is a SQL file that returns 0 rows if things are OK
* You can reuse a macro **inside** a test

### Example:

```sql
SELECT *
FROM {{ ref('housing_prices') }}
WHERE price < 0
```

Save in `tests/test_no_negative_prices.sql`
Run with:

```bash
dbt test --select test_no_negative_prices
```

---

## Exposures – What Are They?

* An **exposure** describes how a model is used, for example in a dashboard, notebook, or report
* It helps with tracking ownership, impact analysis, and documentation

### Common fields:

* `name`: a unique name for the exposure
* `type`: usually `dashboard`, `notebook`, or `analysis`
* `depends_on`: one or more models the exposure uses
* `url`: a link to the dashboard or report (optional)
* `owner`: person responsible for the output (name and email)

---

## Exposures – Example

```yaml
exposures:
  - name: housing_dashboard
    type: dashboard
    depends_on:
      - ref('mart_housing_prices_breakdown')
    owner:
      name: BI Team
      email: bi@example.com
```

---

## Hands-On: Add an Exposure

Open the schema file:

```bash
nano models/gold/schema.yml
```

Add the `exposures:` block from the previous slide.
Save, then re-run docs:

```bash
dbt docs generate
```

View the result:

```bash
dbt docs serve --port 8081 --host 0.0.0.0
```

Visit: [http://localhost:8081](http://localhost:8081)

---

## Hands-On: Add a Test Using Macro Logic (Part 1)

### Step 1: Reuse the macro

Use your `normalize_type()` macro to build a test that fails if the value isn’t one of the expected ones.

Open:

```bash
nano tests/test_unexpected_type.sql
```

Paste:

```sql
SELECT *
FROM {{ ref('stg_location_data') }}
WHERE {{ normalize_type('type') }} = 'UNKNOWN'
```

---

## Hands-On: Add a Test Using Macro Logic (Part 2)

Save, then run:

```bash
dbt test --select test_unexpected_type
```

---

## Hands-On: Create a Macro for Price Buckets (Part 1)

Create a macro that turns price into buckets:

```bash
nano macros/price_bucket.sql
```

---

## Hands-On: Create a Macro for Price Buckets (Part 2)

Write:

```jinja
{% macro price_bucket(price_column) %}
  CASE
    WHEN {{ price_column }} < 200000 THEN 'Low'
    WHEN {{ price_column }} < 400000 THEN 'Medium'
    ELSE 'High'
  END
{% endmacro %}
```

Use it in a model:

```sql
SELECT {{ price_bucket('price') }} as price_range
```

---

## Hands-On: Add a Moving Average Macro to a Gold Model

### Step 1: Create a new macro for moving averages

```bash
nano macros/moving_average.sql
```

Write:

```jinja
{% macro moving_average(value_col, partition_by, order_by, window_size=2) %}
  AVG({{ value_col }}) OVER (
    PARTITION BY {{ partition_by }}
    ORDER BY {{ order_by }}
    ROWS BETWEEN {{ window_size }} PRECEDING AND CURRENT ROW
  )
{% endmacro %}
```

Save and close the file.

---

## Hands-On: Use the Moving Average Macro in a Gold Model

Open:

```bash
nano models/gold/mart_housing_prices_breakdown.sql
```

Add this column:

```sql
{{ moving_average('price', 'region', 'date', 2) }} AS avg_price_last_3
```

Then run:

```bash
dbt run --select mart_housing_prices_breakdown
```

Then inspect with:

```bash
dbt docs serve --port 8081 --host 0.0.0.0
```

---

## Intro to dbt Cloud

* dbt Cloud is a hosted service for dbt projects
* Removes the need for local setup
* Lets you manage and monitor data workflows at scale

We’ll walk through each feature and show you how to explore it in your own Cloud workspace.

* Hosted version of dbt with:

  * Web IDE
  * Scheduled runs
  * Hosted docs
  * Full lineage graph

* Works with GitHub, BigQuery, Snowflake, and more

---

## Create Your Own dbt Cloud Account

* Everyone creates their **own free account** (1 developer seat included)
* Visit: [https://cloud.getdbt.com/signup/](https://cloud.getdbt.com/signup/)
* Use GitHub login if possible (helps with version control)
* Once inside, follow the onboarding to:

  * Create a new project using the **Jaffle Shop** demo project
  * Select **BigQuery** as the warehouse (or ask for help setting this up)
  * Link it to a GitHub repo (optional if you're just exploring)

We’ll use this project to explore dbt Cloud features together.

* Everyone creates their **own free account** (1 developer seat included)
* Visit: [https://cloud.getdbt.com/signup/](https://cloud.getdbt.com/signup/)
* Use GitHub login if possible (helps with version control)
* Once inside, follow the onboarding to:

  * Create a new project (or join one)
  * Connect to a Git repo (we’ll help)

We’ll use this account to explore dbt Cloud features together.

---

## Set Up dbt Cloud (Last Hour)

If you didn’t set up a project during sign-up:

1. Create a new project in dbt Cloud
2. Use the **Jaffle Shop** sample repo

   * GitHub: [https://github.com/dbt-labs/jaffle\_shop](https://github.com/dbt-labs/jaffle_shop)
3. Connect to BigQuery (we’ll help if needed)
4. Run your first job to test the setup

---

---

## Cloud Feature: Cloud IDE

* Navigate to: **Develop** tab in dbt Cloud
* A browser-based IDE where you:

  * Edit models, macros, tests
  * Run models directly
  * Preview results

No local editor needed!

---

## Cloud Feature: Job Scheduling

* Navigate to: **Deploy > Jobs**
* Jobs automate `dbt run`, `dbt test`, etc.
* Set a schedule or trigger manually

Great for running production pipelines.

---

## Cloud Feature: CI/CD Integration

* Navigate to: **Settings > CI/CD**
* When connected to GitHub, dbt Cloud can:

  * Run tests on pull requests
  * Validate model changes before merge

This keeps bad SQL from reaching production.

---

## Cloud Feature: Notifications

* Navigate to: **Settings > Notifications**
* Configure email or Slack alerts for:

  * Failed jobs
  * Successful jobs
  * Cancellations

Keeps your team in the loop.

---

## Cloud Feature: Hosted Docs

* Navigate to: **Docs > Generate Docs**
* dbt Cloud hosts your `dbt docs` UI
* Same content as local `dbt docs serve`, but always accessible

Share links with teammates!

---

## Cloud Feature: Version Control

* Navigate to: **Develop > Git**
* Link your dbt project to GitHub/GitLab/Azure
* Commit and push changes inside dbt Cloud

Works with branches and pull requests.

---

## Cloud Feature: Exposures

* Navigate to: **Docs > Explore > Exposures**
* Define dashboards, notebooks, or tools that depend on models
* Helps track ownership and downstream impact

---

## Cloud Feature: dbt Explorer (DAG View)

* Navigate to: **Docs > Explore > DAG tab**
* Visual graph of your dbt models
* Click a model to see dependencies, SQL, and metadata

---

## Cloud Feature: Semantic Layer (Enterprise only)

* Note: This feature is available on paid tiers
* Define reusable metrics across models
* Central place to align business definitions

---

## Cloud Feature: API Access

* dbt Cloud offers APIs to:

  * Trigger jobs
  * Fetch test results
  * Pull metadata
* Explore: [https://docs.getdbt.com/docs/dbt-cloud/api-v2](https://docs.getdbt.com/docs/dbt-cloud/api-v2)

---

## Wrap-Up 🎓

What you’ve learned today:

* How to make models faster with incrementals
* How to reuse logic using macros
* How to write your own custom tests
* How to define and document exposures
* What dbt Cloud adds to the workflow

Thank you for joining Day 3! 🚀
