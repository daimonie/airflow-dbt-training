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

# Day 3 – Advanced dbt Concepts (Local + Cloud)

---

## Welcome Back!

* What we built yesterday:
  
  * Bronze → Silver → Gold layers
  * Schema tests and documentation
  * dbt docs and lineage

* Where we ended:
  
  * Building gold models with business logic
  * Joining data across sources
  * Creating marts for reporting

Now let's get started optimizing our workflow...

---

## Agenda – Day 3

Morning Session:

1. Incremental models
2. Re-using logic with macros
3. Custom tests and exposures
4. Bringing it all together in a guided project

Afternoon Session:
5. Introduction to dbt Cloud
6. Cloud features and deployment

---

## Recap & Q&A

* What went well yesterday?
* Any issues with:
  * Running models or tests?
  * Model structure or naming?
  * Docs or lineage visibility?

---

## Part 1: Incremental Models

Yesterday we built a Gold mart:

```sql
WITH avg_prices AS (
  SELECT
    region, AVG(price) AS avg_price, COUNT(*) AS n_sales
  FROM {{ ref('stg_housing_prices') }}
  GROUP BY region
)
SELECT
  p.region, p.avg_price, p.n_sales,
  r.urban_count,  r.rural_count, r.pct_urban
FROM avg_prices p
LEFT JOIN {{ ref('region_type_composition') }} r
  ON p.region = r.region
```

That works for the case outlined. But what if we have millions of housing prices? or daily updates to process? Or limited time and budget? 

Enter: **Incremental Models**

---

## Incremental Models – Why?

* Large models don't need to reprocess everything every time
* dbt means you can process **only new or changed rows**
* This can save time and money in production

### Key Trade-off: dbt vs Native Features

While dbt incremental models work across all warehouses, modern data warehouses like Snowflake (Dynamic Tables) and BigQuery (Materialized Views) offer native incremental processing. These built-in features automatically handle updates without requiring dbt runs, often with better performance. However, dbt incrementals give you **more direct control** over transformation logic and timing.

**Key Points - Incremental Models:**

- Incremental models to only process new/changed data
- There are trade-offs between incremental models & native features
- You can add incremental logic to any existing model

---

## Part 2: Reusing Logic with Macros

There are two powerful ways to reuse logic in dbt:

- **Macros**: Reusable SQL/Jinja snippets
- **Custom Tests**: Reusable data quality checks

Let's explore how to build and use both effectively!

---

## When to Use a Macro

Consider using a macro when you see:

1. **Repeated Logic Patterns**
   
   * Same CASE statement structure across models
   * Similar aggregation patterns in multiple places
   * Identical WHERE clause conditions

2. **Complex Transformations**
   
   * Multi-step value normalization
   * Date/time calculations that you use often
   * Window functions with consistent patterns

---

## When to Use a Macro Pt 2

3. Business Logic That Might Change**
* Status mappings that could evolve
* Categorization rules that may need updating
* Thresholds that might be adjusted

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

---- 

## When to Use a Macro Pt 3

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

We used this line at the top of the model file:

```jinja
{{ config(materialized='incremental', unique_key='id') }}
```

Here's what it means:

* `materialized='incremental'` tells dbt to treat this model as **incremental** — after the first run, it only adds or updates new data.
* `unique_key='id'` tells dbt how to match rows, which avoids duplicates.

This line uses **Jinja**, the dbt's templating language. 

 Jinja inserts logic or configuration into SQL files. Everything is interpreted by dbt first, not directly by the database.

---

## Run the Incremental Model (Part 1)

### Step 1: Initial State - Check Current Data

First, let's see how many rows we have:

```sql
SELECT COUNT(*) FROM silver.incremental_prices;
```

Make a note of this number, we'll compare after updates.

Run the model for the first time:

```bash
dbt run --select incremental_prices
```

Verify that it says `materialized: incremental`

---

## Run the Incremental Model (Part 2)

### Step 2: Process Updated Data

Now rerun the model to register the changes we made:

```bash
dbt run --select incremental_prices
```

What to watch for:

* Model should report "10 rows affected"
* Run time should be quick (only processing changed rows)
* Total row count should stay the same

Why? Because incremental models only process new/changed data.

---

## Run the Incremental Model (Part 3)

### Step 3: Verify Incremental Logic

Run the model one more time to verify our logic:

```bash
dbt run --select incremental_prices
```

* This run should complete very quickly
* You should see "0 rows affected" in the output
* This confirms our incremental logic is working and no unchanged rows are being reprocessed

---------

## Run the Incremental Model (Part 3)

### Verify Row Counts

Let's confirm our data is correct:

```sql
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as distinct_ids
FROM silver.incremental_prices;
```

The counts should match, confirming:

* We haven't created any duplicates
* All our data is present
* The incremental logic is working as expected

---

## Understanding What We've Verified

Through these runs, we've confirmed:

1. **Efficiency**
   
   * First run: Created initial table
   * Second run: Processed only updated rows
   * Third run: Processed 0 rows (perfect!)

2. **Data Quality**
   
   * No duplicates created
   * All updates captured
   * Original data preserved

3. **Production Readiness**
   
   * Model handles updates correctly
   * Processing is efficient
   * Safe to use in production

This pattern of testing is crucial when developing incremental models because it ensures they'll work reliably in production.

---

## Simulate Updated Data (Part 1)

To simulate new data, we'll update 10 rows in the **source table**.

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

This changes the `updated_at` field for 10 random rows.

Now, we'll rerun the model to register those changes.

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

Return to the `dwh` container and connect:

```bash
psql -h localhost -U postgres -d dwh
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
* Run it **again** to confirm that it only adds new data

---

## First Macro: Value Normalization

Let's start with a common need: standardizing values across models.

### Step 1: Create the Macro

```bash
nano macros/normalize_values.sql
```

```jinja
{%- macro normalize_values(column_name, accepted_values) -%}
    CASE
        {%- for value in accepted_values %}
        WHEN LOWER({{ column_name }}) = LOWER('{{ value }}') THEN '{{ value }}'
        {%- endfor %}
        ELSE 'UNKNOWN'
    END
{%- endmacro -%}
```

---

## Using normalize_values

The normalize_ values macro provides powerful standardization capabilities:

Example usage in a model:

```sql
SELECT 
    id,
    {{ normalize_values('type', ['URBAN', 'RURAL', 'SUBURBAN']) }} as normalized_type,
    {{ normalize_values('status', ['ACTIVE', 'INACTIVE', 'PENDING']) }} as normalized_status
FROM {{ ref('raw_data') }}
```

---

## normalize_values: Key Features

- **Flexible Inputs**
  
  - Takes any column name and list of accepted values
  - Can be used on any text column needing standardization

- **Smart Processing**
  
  - Case-insensitive matching for input values
  - Standardizes output to the exact casing provided
  - Returns 'UNKNOWN' for any unmatched values

- **Reusability**
  
  - Use across different models and columns
  - Maintain consistent value handling
  - Single source of truth for value normalization

---

## Building on normalize_values: A Pivoting Macro

Now that we can normalize values, let's count them efficiently.

### Goal

Create a macro that generates pivot counts for any enum column

### Specifications

- Name: `pivot_enum_values`
- Inputs:
  - `column_name`: Column to pivot on (e.g. `"type"`)
  - `values`: List of values to pivot (e.g. `['URBAN', 'RURAL']`)
- Output: Generated SQL with one count per value

**Hint**: Use a Jinja loop to generate the counts  
**Bonus Challenge**: Make total count optional with a parameter

---

## Pivoting Macro: Solution

```jinja
{% macro pivot_enum_values(column_name, values, include_total=true) %}
  {% for val in values %}
    COUNT(*) FILTER (WHERE {{ normalize_values(column_name, [val]) }} = '{{ val }}') AS {{ val | lower }}_count
    {%- if not loop.last %},{% endif %}
  {% endfor %}
  {%- if include_total %}
    {%- if values|length > 0 %},{% endif %}
    COUNT(*) AS total_count
  {%- endif %}
{% endmacro %}
```

Notice how we reuse `normalize_values` inside our new macro!

---

## Using Macros in Tests

Now that we have robust value handling, let's ensure data quality.

### Custom Generic Test

```sql
-- tests/generic/test_valid_values.sql
{% test valid_values(model, column_name, valid_values) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ normalize_values(column_name, valid_values) }} = 'UNKNOWN'
{% endtest %}
```

### Usage in schema.yml

```yaml
models:
  - name: stg_location_data
    columns:
      - name: type
        tests:
          - valid_values:
              valid_values: ['URBAN', 'RURAL']
```

--- 

## Advanced: Integration Tests

We can also use dbt to validate relationships between models:

* Test entire data pipelines, not just individual models
* Catch issues that schema tests might miss
* Protect business-critical transformations

---

## Example: Row Count Consistency

```sql
-- tests/test_row_consistency.sql
SELECT 'Mismatch' AS issue
WHERE (
  SELECT COUNT(*) FROM {{ ref('mart_housing_prices_breakdown') }}
) != (
  SELECT COUNT(DISTINCT region, date) FROM {{ ref('stg_housing_prices') }}
)
```

This ensures:

- No rows were duplicated or dropped
- The mart model is consistent with staging

---

## More Integration Test Ideas

Common patterns to consider:

1. **Join Key Validation**
   
   - No NULLs in join columns
   - No missing references

2. **Aggregation Checks**
   
   - Totals match across models
   - No unexpected nulls in aggregates

3. **Business Logic**
   
   - Filtering didn't exclude key records
   - Calculations remain consistent

**Why it matters**: Protects business-critical data pipelines from subtle bugs.

---

## Extension Ideas

Here are some ways to build on these patterns:

### Macro Enhancements

- Add custom column name suffixes/prefixes
- Support for percentage calculations
- Allow custom aggregations beyond COUNT
- Add value validation against a source

### Test Extensions

- Check for unexpected value combinations
- Validate value distributions
- Compare values across time periods

---

## Custom Tests in dbt

You can write custom tests and reuse them for all models across your project.

* A **custom test** is an SQL file that returns 0 rows if things are OK
* Like macros, custom tests are reusable across your project
* You can even use macros inside your custom tests!

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
* Exposures are defined in your `schema.yml` files, typically alongside the models they reference

### Common fields:

* `name`: a unique name for the exposure
* `type`: usually `dashboard`, `notebook`, or `analysis`
* `depends_on`: one or more models the exposure uses
* `url`: a link to the dashboard or report (optional)
* `owner`: person responsible for the output (name and email)

---

## Step 1: Choose the Right Location

Exposures should be defined in the same schema file as their primary source model. In our case, since we're exposing the `mart_housing_prices_breakdown` model, we'll add it to:

```bash
nano models/gold/schema.yml
```

---

## Step 2: Add the Exposure Definition

Add this exposure block at the bottom of `models/gold/schema.yml`, after your model definitions:

```yaml
# models/gold/schema.yml

# ... existing model definitions remain unchanged ...

exposures:
  - name: housing_dashboard
    type: dashboard
    depends_on:
      - ref('mart_housing_prices_breakdown')
    owner:
      name: BI Team
      email: bi@example.com
    url: https://metabase.example.com/dashboard/123
    description: >
      Daily housing market KPIs showing:
      - Average prices by region
      - Sales volume trends
      - Listing status distribution
    maturity: medium  # Options: low, medium, high
```

### Step 3: Verify Documentation

Generate and view the updated documentation:

```bash
dbt docs generate
dbt docs serve --port 8081 --host 0.0.0.0
```

Visit: [http://localhost:8081](http://localhost:8081)

In the docs, you should now see:

* The exposure listed under the Gold package
* A clear link to the source model
* The full description and ownership details

**Note**: Keep exposures close to their primary source models. If you have multiple schema files, add each exposure to the schema file that contains its main source model. This makes maintenance easier and relationships clearer.

---

## Hands-On: Add a Test Using Macro Logic (Part 1)

### Step 1: Reuse the macro

Use your `normalize_values()` macro to build a test that fails if an unexpected value is returned.

Open:

```bash
nano tests/test_unexpected_type.sql
```

Paste:

```sql
SELECT *
FROM {{ ref('stg_location_data') }}
WHERE {{ normalize_values('type', ['URBAN', 'RURAL', 'SUBURBAN']) }} = 'UNKNOWN'
```

Save

---

## Hands-On: Add a Test Using Macro Logic (Part 2)

Run:

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

Run:

```bash
dbt run --select mart_housing_prices_breakdown
```

Inspect with:

```bash
dbt docs serve --port 8081 --host 0.0.0.0
```

---

## dbt Artifacts: Under the Hood

Every time you run dbt, it produces structured metadata in JSON format:

| File               | Purpose                                     |
| ------------------ | ------------------------------------------- |
| `manifest.json`    | All models, tests, sources, refs, macros    |
| `run_results.json` | Execution results: timing, status, errors   |
| `catalog.json`     | Column-level metadata and types (from docs) |

You can find data here:

```bash
target/manifest.json
target/run_results.json
target/catalog.json
```

**Note**: Compiled sql queries are available in dbt docs and in the compiled/ folder

---

## Morning Project: Extend Your Gold Mart!

Now that we've learned about incrementals, macros, tests, and exposures, let's bring it all together!

Let's apply everything we've learned to improve our housing price mart.

### Goals

1. Make the mart incremental
2. Add standardized status tracking
3. Add proper testing
4. Document everything

---

## Step 1: Make Your Mart Incremental

Convert `mart_housing_prices_breakdown` to process incrementally:

```sql
{{ config(
    materialized='incremental',
    unique_key=['region', 'date']
) }}

WITH avg_prices AS (
  SELECT
    region, 
    date,
    AVG(price) AS avg_price,
    COUNT(*) AS n_sales
  FROM {{ ref('stg_housing_prices') }}
  {% if is_incremental() %}
  WHERE date > (SELECT MAX(date) FROM {{ this }})
  {% endif %}
  GROUP BY region, date
)
-- ... rest of your existing joins ...
```

---

## Step 2: Add Status Tracking

1. Create a status normalization macro:
   
   ```sql
   -- macros/normalize_status.sql
   {%- macro normalize_status(status_column) -%}
   {{ normalize_values(status_column, ['LISTED', 'PENDING', 'SOLD']) }}
   {%- endmacro -%}
   ```

2. Add status tracking to your mart:
   
   ```sql
   SELECT 
    -- ... existing columns ...
    {{ normalize_status('status') }} as listing_status,
    {{ pivot_enum_values('status', ['LISTED', 'PENDING', 'SOLD']) }}
   FROM {{ ref('stg_housing_prices') }}
   GROUP BY region, date
   ```

---

## Step 3: Add Tests - Part 1

Let's start by adding a proper unique identifier to our model:

```sql
-- models/mart_housing_prices_breakdown.sql
WITH source_data AS (
    -- ... existing WITH clauses ...
)

SELECT 
    CONCAT(region, '_', date::text) as region_date_id,  -- Add this unique identifier
    region,
    date,
    avg_price,
    n_sales,
    listing_status,
    listed_count,
    pending_count,
    sold_count
FROM source_data
```

Why add a unique identifier?

* Makes the uniqueness constraint explicit in the data
* Creates a reliable joining key for downstream models
* Easier to test and maintain

---

## Step 3: Add Tests - Part 2

Now let's add basic tests to your `schema.yml`:

```yaml
models:
  - name: mart_housing_prices_breakdown
    description: "Daily housing prices by region with area composition"
    columns:
      - name: region_date_id
        description: "Unique identifier combining region and date"
        tests:
          - unique
          - not_null
```

These tests ensure:

* Each region/date combination appears only once
* We never have missing identifiers

---

## Step 3: Add Tests - Part 3

Add relationship and value tests:

```yaml
models:
  - name: mart_housing_prices_breakdown
    columns:
      - name: region 
        tests:
          - not_null
          - relationships:
              to: ref('stg_location_data')
              field: region

      - name: listing_status 
        tests:
          - valid_values:
              valid_values: ['LISTED', 'PENDING', 'SOLD']
```

These tests verify:

* Regions exist in our location data
* Status values are from our allowed set

---

## Step 3: Add Tests - Benefits

This testing approach provides several advantages:

1. **Better Data Structure**
   
   * Unique identifiers are part of the model
   * Constraints are visible in the data

2. **Improved Testing**
   
   * Simple, focused tests
   * Easy to understand and maintain
   * Clear test failure messages

3. **Downstream Benefits**
   
   * Reliable joining key available
   * Clear documentation
   * Visible data constraints

---

## Step 4: Document Everything

Update your`schema.yml`:

```yaml
models:
  - name: mart_housing_prices_breakdown
    description: "Daily housing prices by region with area composition"
    columns:
      - name: region
        description: "Geographic region identifier"
      - name: date
        description: "Date of the price records"
      - name: avg_price
        description: "Average house price in the region for this date"
      - name: n_sales
        description: "Number of sales in this region/date"
      - name: listing_status
        description: "Normalized status of the listing"
      - name: listed_count
        description: "Number of houses currently listed"
      - name: pending_count
        description: "Number of houses with pending sales"
      - name: sold_count
        description: "Number of completed sales"
```

---

## Step 5: Create an Exposure

Add to your `schema.yml`:

```yaml
exposures:
  - name: regional_housing_dashboard
    type: dashboard
    description: Daily housing market overview showing prices, sales volumes, and listing status by region
    depends_on:
      - ref('mart_housing_prices_breakdown')
    owner:
      name: Analytics Team
      email: analytics@company.com
    url: https://your-bi-tool.company.com/housing-dashboard
    maturity: medium
```

**Morning Session Progress:**

- You've learned how to:
  - Make models process incrementally
  - Create reusable logic with macros
  - Write custom tests
  - Document and expose your work

---

## Afternoon Session: dbt Cloud

dbt Cloud is a hosted service for dbt projects:

- - Web IDE
  - Scheduled runs
  - Hosted docs
  - Full lineage graph
  - Works with GitHub, BigQuery, Snowflake, and more

dbt CLoud: 

* Removes the need for local setup
* Lets you manage and monitor data workflows at scale

We'll walk through each feature and show you how to explore it in your own Cloud workspace.



---

## Create Your Own dbt Cloud Account

Set you your **own free account** (1 developer seat included)

* Visit: [https://cloud.getdbt.com/signup/](https://cloud.getdbt.com/signup/)

* Use GitHub login if possible (improves version control)

* Once set up, follow the onboarding to:
  
  * Create a new project using the **Jaffle Shop** demo project
  * Select **BigQuery** as the warehouse (or ask for help setting this up)
  * Link it to a GitHub repo (optional if you're just exploring)

We'll use this project to explore dbt Cloud features together.

---

## Set Up dbt Cloud (Last Hour)

If you didn't set up a project during sign-up:

1. Create a new project in dbt Cloud

2. Use the **Jaffle Shop** sample repo
   
   * GitHub: [https://github.com/dbt-labs/jaffle\_shop](https://github.com/dbt-labs/jaffle_shop)

3. Connect to BigQuery (we'll help if needed)

4. Run your first job to test the setup

---

## Cloud Feature: Cloud IDE

* Navigate to: **Develop** tab in dbt Cloud  

* Explore the in-browser IDE where you can:
  
  - Edit models, macros, schema.yml, and tests  
  - Preview SQL compilation and run results  
  - Access model documentation via the right panel

**Try this**:  

- Open a model and inspect the compiled SQL
- Modify a model and run it directly from the UI
- Check the logs and preview the table output

**Why it matters**: You get reproducible development without needing a local setup — perfect for shared team environments.

---

## Cloud Feature: Job Scheduling

* Navigate to: **Deploy > Jobs**  

* Jobs automate workflows:
  
  - `dbt run`, `dbt test`, `dbt build`
  - Commands triggered on a schedule or manually
  - Environment-specific configs (prod vs dev)

**Try this**:  

- Create a job that runs models daily at 08:00
- Add `dbt test` as a follow-up command
- Run manually and inspect job logs

**Why it matters**: Scheduled jobs replace cron scripts and orchestrators for many teams — clean, visible, and easy to debug.

---

## Cloud Feature: CI/CD Integration

* Navigate to: **Settings > CI/CD**  
* Integrate with GitHub, GitLab, or Azure DevOps  
* dbt Cloud automatically runs jobs on pull requests 

### Typical Development Flow:

1. **Create Feature Branch & Make Changes**
   
   ```bash
   git checkout -b feature/add-model
   # Edit models, tests, docs
   ```

2. **Open PR & Let CI Run**
   
   * Push changes & create PR
   * dbt Cloud detects PR and runs tests
   * ✅ Success = Ready to merge
   * ❌ Failure = Fix issues first
   * 
     
     **Why it matters**: Automates testing before changes reach production. This ensures code quality and data integrity to maintain standardized and complete deployments.

---

## dbt Cloud with On-Premise Data

Need to connect dbt Cloud to on-premise databases? You have options:

1. **Allowlisted IPs** (Simplest): Allow specific dbt Cloud IPs through your firewall
   
   * See [docs.getdbt.com](https://docs.getdbt.com/docs/dbt-cloud/cloud-configuring-dbt-cloud/ip-addresses)

2. **SSH Tunnel** (Common): Use a bastion host for secure access
   
   * Requires some infrastructure setup

3. **Fully Isolated?**: Use dbt Core + Airflow (like we learned!)
   
   * Perfect for isolated environments
   * Gives you full control over scheduling

**Remember***: Always involve your security team when connecting cloud services to on-premise data.

---

## Cloud Feature: Notifications

* Navigate to: **Settings > Notifications**  

* Configure alerts for:
  
  - Failed or successful jobs
  - Job cancellations or delays

**Try this**:  

- Add a Slack webhook or email address
- Trigger a job failure (e.g. by testing an invalid ref)
- Confirm alert delivery

**Why it matters**: Teams stay informed without manual checking, building trust and reliability in the data pipeline.

---

## Cloud Feature: Hosted Docs

Hosted `dbt docs serve` are always available

* Navigate to: **Docs > Generate Docs**  

**Try this**:  

- Generate docs and open the lineage graph
- Click through a model and inspect its description, columns, and tests
- Search for an exposure and see dependencies

**Why it matters**: Centralizes documentation so model structure is transparent across teams with no local server needed.

---

## Cloud Feature: Version Control

* Navigate to: **Develop > Git**  
* Link your project to a Git provider  
* Edit, commit, and push directly from the IDE

**Try this**:  

- Create a new branch and make a model edit
- Commit the change and push to GitHub
- Open a PR and let CI kick in

**Why it matters**: Treats data code like software — versioned, reviewed, and controlled. Aligns with modern SDLC practices.

---

## Cloud Feature: Exposures

* Navigate to: **Docs > Explore > Exposures**  
* Define dashboards, notebooks, or reports that use dbt models

**Try this**:  

- Add a new exposure in `schema.yml`
- Use `depends_on` to link a gold model
- Refresh docs and view it in the UI

**Why it matters**: Tracks downstream usage and ownership so data lineage goes all the way to dashboards and reports.

---

## Cloud Feature: dbt Explorer (DAG View)

* Navigate to: **Docs > Explore > DAG tab**  
* See a visual graph of all dbt models and dependencies

**Try this**:  

- Click a staging model and see what it feeds into
- Explore top-down from a mart to understand its lineage
- Hover to preview SQL or click into model details

**Why it matters**: Helps explain your pipeline to non-engineers and supports debugging and dependency impact analysis.

---

## Cloud Feature: Semantic Layer (Enterprise Only)

* Only available on paid tiers  
* Lets you define centralized metrics using `metrics:` blocks

**Key concepts**:

- Reusable definitions like `total_revenue` or `conversion_rate`
- Queryable from BI tools via dbt's API

**Why it matters**: Aligns business logic across dashboards, tools, and teams — no more conflicting definitions of "active users."

---

## Cloud Feature: API Access

* dbt Cloud offers APIs for automation and integration

**Explore the docs**:  
[https://docs.getdbt.com/docs/dbt-cloud/api-v2](https://docs.getdbt.com/docs/dbt-cloud/api-v2)

**Common use cases**:

- Trigger jobs from external systems (e.g. Airflow, Slackbot)
- Pull metadata for lineage visualization
- Retrieve run logs or test results programmatically

**Why it matters**: Opens up dbt Cloud to custom orchestration and monitoring tools which is great for advanced users and platform teams.

---

## Wrap-Up

What you've learned today:

* How to make models faster with incrementals
* How to reuse logic using macros
* How to write your own custom tests
* How to define and document exposures
* What dbt Cloud adds to the workflow fair 
