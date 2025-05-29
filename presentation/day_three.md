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

Now let's optimize our workflow...

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

Yesterday we built our gold mart:
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
* dbt lets you process **only new or changed rows**
* This can save time and money in production

### Key Trade-off: dbt vs Native Features

While dbt incremental models work across all warehouses, modern data warehouses like Snowflake (Dynamic Tables) and BigQuery (Materialized Views) offer native incremental processing. These built-in features automatically handle updates without requiring dbt runs, often with better performance. However, dbt incrementals give you more direct control over the transformation logic and timing.

**Key Points - Incremental Models:**
- Incremental models to only process new/changed data
- There are trade-offs between incremental models & native features
- You can add incremental logic to any existing model

---

## Part 2: Reusing Logic with Macros

Two powerful ways to reuse logic in dbt:
- **Macros**: Reusable SQL/Jinja snippets
- **Custom Tests**: Reusable data quality checks

Let's explore how to build and use both effectively!

---

## When to Use a Macro

Consider creating a macro when you see:

1. **Repeated Logic Patterns**
   * Same CASE statement structure across models
   * Similar aggregation patterns in multiple places
   * Identical WHERE clause conditions

2. **Complex Transformations**
   * Multi-step value normalization
   * Date/time calculations that you use often
   * Window functions with consistent patterns

3. **Business Logic That Might Change**
   * Status mappings that could evolve
   * Categorization rules that may need updating
   * Thresholds that might be adjusted

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

### Step 1: Initial State - Check Current Data

Let's check our starting data. First, connect to the database:

1. Open **Docker Desktop**
2. Click on **Containers** in the left sidebar
3. Find and click on the `dwh` container
4. Click the **Terminal** tab
5. Connect to the database:
   ```bash
   psql -h localhost -U airflow -d dwh
   ``` 
---
## Row Count
Now check the current row count:
```sql
-- First, let's see what tables we have:
\dt public_silver.*

-- Then check our table:
SELECT COUNT(*) 
FROM public_silver.incremental_prices;

-- To see some sample data:
SELECT * 
FROM public_silver.incremental_prices 
LIMIT 5;
```

If you don't see the table yet, that's expected! We haven't run our dbt model for the first time. Let's do that now:

```bash
dbt run --select incremental_prices
```

Check that it says `materialized: incremental`

---

## Run the Incremental Model (Part 2)
###  Initial count
Now check the current row count:
```sql
SELECT COUNT(*) FROM public_silver.incremental_prices;
```

Remember this number - we'll compare after our updates.

Now run the model for the second time:

```bash
dbt run --select incremental_prices
```

Check that it says `materialized: incremental`

---

## Verify Row Counts

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

Example usage in a model:
```sql
SELECT 
    id,
    {{ normalize_values('type', ['URBAN', 'RURAL', 'SUBURBAN']) }} as normalized_type,
    {{ normalize_values('status', ['ACTIVE', 'INACTIVE', 'PENDING']) }} as normalized_status
FROM {{ ref('raw_data') }}
```
Let's apply this macro to our staging model for location data:

---

## normalize_values: Key Features

The macro provides powerful standardization capabilities:

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

Let's use it in our `gold.region_type_composition` model!

---

## Documenting macros and setting variables
You can set variables for your model at the top:
```
{% set option_1='RURAL'}
{% set option_2='URBAN'}
```
Use them normally in your model: ` {{ option_1 }}

Document your macros by using a schema in the `dbt/macros` folder:
```
version 2:
macros:
  - name: normalize_values
    description: Normalizes values to the given values
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
To see the results, either find compiled query or use `dbt test --store-failures`
--- 

## Advanced: Integration Tests

Beyond column-level tests, we can validate relationships between models.

* Test entire data pipelines, not just individual models
* Catch issues that schema tests might miss
* Protect business-critical transformations

---

## Example: Row Count Consistency
Integration testing can be done with a custom test:
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

## dbt Artifacts: Under the Hood

Every time you run dbt, it produces structured metadata in JSON format:

| File | Purpose |
|------|---------|
| `manifest.json` | All models, tests, sources, refs, macros |
| `run_results.json` | Execution results: timing, status, errors |
| `catalog.json` | Column-level metadata and types (from docs) |

You can find them here:

```bash
target/manifest.json
target/run_results.json
target/catalog.json
```

Note: And as we previously mentioned, the compiled sql queries will be available in dbt docs and in the compiled/ folder

## dbt Cloud

* dbt Cloud is a hosted service for dbt projects
* Removes the need for local setup
* Lets you manage and monitor data workflows at scale

* Hosted version of dbt with:
  * Web IDE
  * Scheduled runs
  * Hosted docs
  * Full lineage graph

* Works with GitHub, BigQuery, Snowflake, and more

---

## Create Your dbt Cloud Account
* Create your **free account** (1 developer seat included)
* Visit: [https://cloud.getdbt.com/signup/](https://cloud.getdbt.com/signup/)
* Use GitHub login (recommended for easier setup)
   * Or make a github login

---

## Project Setup
1. Create new project in dbt Cloud
2. Connect to BigQuery:
   * You'll need service account credentials (provided via Pastebin)
   * Add credentials in connection setup
   * Test connection
3. Clone Jaffle Shop repo:
   * [github.com/dbt-labs/jaffle-shop](https://github.com/dbt-labs/jaffle-shop)

---

## First Steps in dbt Cloud
1. Open project in Cloud IDE
2. Run initial commands:
   ```bash
   dbt deps
   dbt debug
   dbt compile
   ```
3. Verify successful setup in logs

---

## Cloud IDE Overview
* **File Navigation**: Browse project structure
* **SQL Editor**: Write and edit models
* **Command Bar**: Run dbt commands
* **Git Integration**: Manage versions
* **Preview**: See compiled SQL

**Try this**:
- Open a model and inspect the compiled SQL
- Modify a model and run it directly
- Check the logs and preview results

---

## Working with Models
* Open existing models
* Create new models
* Run specific models:
  ```bash
  dbt run --select model_name
  dbt test --select model_name
  ```
* View results in the UI

---

## Documentation & Lineage
* Generate docs: `dbt docs generate`
* View in **Docs** tab:
  - DAG visualization
  - Model details
  - Column descriptions
  - Dependencies

**Try this**:
- Generate docs and explore the lineage graph
- Click through model relationships
- Search for specific models or columns

---

## Explorer (DAG View)
* Interactive model exploration
* Visual dependency mapping
* Click through capabilities:
  - See upstream/downstream models
  - Preview SQL code
  - Check test status
  - View documentation

**Try this**:
- Start from a mart model and trace its sources
- Identify critical path dependencies
- Use the search and filter options

---

## Development Workflow
1. Create feature branch
2. Make changes in IDE
3. Test locally: `dbt test`
4. Commit and push
5. Create PR
6. Automated CI runs
7. Review & merge

---

## Job Scheduling
* Create jobs in **Deploy > Jobs**
* Common job types:
  - Daily full refresh
  - Incremental updates
  - Test runs
* Set schedule and notifications

**Try this**:
- Create a daily refresh job
- Add test commands
- Configure notifications

---

## Environments
* Development
  - Personal schema
  - Rapid iteration
  - Direct feedback
* Production
  - Scheduled jobs
  - Stable schemas
  - Monitored execution

---

## Connecting to On-Premise Data
Three main options for connecting dbt Cloud to internal databases:

1. **Allowlisted IPs**
   * Whitelist dbt Cloud IP ranges
   * Simplest approach
   * Requires firewall access

2. **SSH Tunnel**
   * Secure connection via bastion
   * More setup required
   * Better security

---

## On-Premise Setup Options
3. **Hybrid Setup**
   * Use dbt Core locally
   * Connect via internal network
   * Full control over connectivity

Remember: Always involve security team when connecting cloud services to internal data.

---

## CI/CD Integration
* Automated testing on pull requests
* Branch-specific deployments
* Status checks in GitHub/GitLab

**Development Flow**:
1. Branch → Change → Push
2. PR triggers dbt Cloud runs
3. Tests must pass to merge

---

## Schema Management
* Use Jinja for dynamic schemas:
  ```sql
  {{ config(schema=env_var('DBT_SCHEMA', target.schema + '_mart')) }}
  ```
* Development schemas per user
* Production schemas stay stable

---

## Enterprise Features
* Semantic Layer
  - Define metrics once
  - Use across all BI tools
* SSO Integration
* Advanced permissions
* Custom deployments

---

## Monitoring & Alerts
* Job status notifications
* Failure alerts
* Success confirmations
* Integration options:
  - Email
  - Slack
  - Custom webhooks

---

## API Integration
* REST API for automation
* Common use cases:
  - Trigger jobs programmatically
  - Fetch run status
  - Get model metadata
  - Integrate with other tools

**Try this**:
- Review API documentation
- Test an API endpoint
- Plan potential integrations

---

## Tips for Success
* Use meaningful branch names
* Regular small commits
* Test before pushing
* Monitor job durations
* Keep documentation updated
