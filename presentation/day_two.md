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

# Airflow and dbt

## Day two: Intro to dbt

### WIFI 2f4o9r1eAC [console.cloud.google.com](http://console.cloud.google.com)

### Josko de Boer

--- 

## Agenda

* Introduction to dbt (30 min)
  
  * Core concepts and project setup
  * Development environment

* Building Our First Models (1h)
  
  * Creating staging models
  * Writing and testing SQL

* Advanced dbt Features (1h)
  
  * Materializations and marts
  * Dependencies and DAG structure

* Testing and Documentation (45 min)
  
  * Writing tests and docs

---

## A Long Time Ago in a Company Far Away

We had over 5k manually made views, with extensive user analytics to track product use how it overlapped with general finance. We were facing problems including: 

- Disjointed ETLs: Ingestion & Transformation were handled in 10+ tools

- 5,000+ manual views 

- Automations were run from local computers
  
  

Most of these problems were non-standardized sql-to-sql transformations

------------



## Introduction to dbt – Why it Matters

(Add brief introduction)

* * Like many teams, we had SQL transformations scattered across dashboards, scripts, and notebooks.
  * They were difficult to maintain, test, or understand.
  * We wanted to treat SQL more like code — with dependencies, version control, and clear structure. Enter **dbt**

---

## Introduction to dbt – What Is It?

DBT is a transformation tool for analytics engineers.

* What problems does dbt solve?
  
  * In many analytics workflows, SQL transformations are scattered across BI tools, spreadsheets, notebooks, and pipelines — making versioning, testing, and collaboration difficult.
  * dbt solves this by transforming SQL into a software development workflow.

* dbt is SQL-first, code-based, version-controlled, and testing-focused.

---

## Introduction to dbt: Use Cases

* Building clean, modular data pipelines in SQL.
* Building and testing trustworthy transformations.
* Simplifying team collaboration on data code.
* Automating documentation and dependency tracking.
* Creating reliable data marts that feed dashboards.
* Supporting analytics engineering as a practice.

---

## Introduction to dbt: vs. Common Alternatives

* **Using database views in**:
  
  * Fast to set up but hard to version or test.
  * No built-in dependency tracking or documentation.

* **Scheduled scripts or procedures**:
  
  * Common in legacy pipelines.
  * Often scattered, untested, and hard to debug or extend.

* **Manually wiring Airflow DAGs**:
  
  * Powerful but verbose.
  * Low-level and not focused on data modeling or testing.

---

## Introduction to dbt: How dbt Helps

Modular, version-controlled, and tested SQL:

* Treats SQL like code: modular, version-controlled, tested.
* Automatically builds workflows using `ref()` to determine dependencies.
* Integrates testing, documentation, and lineage into the workflow.

---

## Models (SQL files)

Each dbt model is a `.sql` file defining a transformation using a SELECT statement.

* dbt turns these into views or tables in your data warehouse.
* Logic is clean and modular with one transformation per file.
* Models can be extensively configured (more on Day 3)



---

## Ref and Dependency Graph

dbt uses `ref()`to build connected workflows with models.

1. `ref()` links models together.
2. Linked models automatically build a dependency graph.
3. dbt uses the graph to determine run order.
4. You get a workflow without writing orchestration code.

---

## Materializations

Materializations define how dbt creates outputs for each model.

* Options include:
  
  * `**view**`: re-runs every time.
  * `**table**`: persistent snapshot of results.
  * `**incremental**`: only updates new data on each run.

* You choose the materialization per model.

---

## Sources and Seeds

dbt allows you to leverage data already in your warehouse or manually upload master data: 

* **Sources** are external data already in your warehouse.
  
  * Declares where raw tables live.
  * Adds lineage and testing for upstream data.

* **Seeds** are CSV files that are loaded as tables.
  
  * Builds reference data & small lookup tables.

---

## Testing

Tests allow you to catch issues early and keep data quality in check. 

dbt  has two types of **tests** diectly integrated into the workflow: 

* Built-in tests: `not_null`, `unique`, `accepted_values`, `relationships`
  - `unique`: tests for unique data.
  
  - `not_null`: tests for data without null values.
  
  - `accepted_values`: tests data against a set such as 'placed', 'shipped', 'completed', or 'returned'.
  
  - `relationships`: tests for referential integrity / one-sided normalization.
* Custom tests: SQL queries that should return zero rows.
  
  

---

## Documentation and Lineage

dbt allows you to automate documentation and lineage for your workflow: 

* dbt generates interactive docs from projects.
  
  * Shows columns, descriptions, tests, and relationships.

* dbt generates Lineage from your models 
  
  * Links dependencies across models 

---

## Jinja in dbt (with Example)

Jijnja is useful for avoiding repetition and introducing templating to dbt.

- Add logic to SQL including loops, variables, conditions.

- Create your own macro
* Example usage inside a model:

```sql
SELECT *
FROM {{ source('weather', 'daily') }}
WHERE region = '{{ var("region", "north") }}'
```

---

## Medallion Architecture – The Concept

Medallion Architecture encourages a clear separation of concerns and reproducibility.

Medallion Architecture is a three-layer pattern for organizing data workflows:

* **Bronze**: raw, ingested data
* **Silver**: cleaned and standardized data, one source at a time
* **Gold**: joined data, business-level aggregates and facts

<center>
<img src="/home/marp/app/medallion_architecture.png" alt="Medallion Architecture Diagram" width="600"/>
</center>

Gaining traction in the industry — highlighted in the recent O'Reilly book by Piethein Strengholt, former Microsoft NL CDO and now leading at Nationale Nederlanden.

---

## Bronze Layer – Raw Ingestion

The Bronze Layer is the **Landing Zone**: It acts as the **immutable archive** for raw data.

* Key characteristics:
  
  - Store data exactly as received from source systems.
  - Only add metadata (like ingestion timestamps).
  - Never modify after ingestion.
  - Serves as single source of truth.

* Examples:
  
  * Raw CSV load from CBS.
  * API snapshots (point-in-time copies of API responses, preserving exact data from external services).
- These raw data sources form a foundation for further transformations by providing a clean archive so data can be reprocessed as downstream logic changes and multiple teams can work independently using the same source. 

---

## Creating Bronze Models (Housing Prices)

* In the terminal, run:

```bash
nano models/bronze/housing_prices.sql
```

* Paste:

```sql
SELECT *
FROM public.raw_housing_prices
```

* Save with `Ctrl+X`, then `Y`, then `Enter`

---

## Creating Bronze Models (Location Data)

Repeat for location data:

```bash
nano models/bronze/location_data.sql
```

```sql
SELECT *
FROM public.raw_location_data
```

---

## Run and Inspect Bronze Models

* Run the following to build your models:

```bash
dbt run
```

* Check for output in the database (e.g. `housing_prices`, `location_data` as views)

---

## Schema Example – Bronze Layer

dbt uses `schema.yml`to define model metadata including tests, descriptions, and sources. This is reflected in every layer of the Medallion Architecture. 

In the Bronze layer: 

* `schema.yml` defines sources and tests for raw data.

```yaml
version: 2
sources:
  - name: public
    tables:
      - name: raw_housing_prices
        columns:
          - name: id
            tests: [not_null, unique]
```

---

## Full schema.yml – raw\_housing\_prices

```yaml
version: 2

sources:
  - name: public
    database: dwh
    schema: public
    tables:
      - name: raw_housing_prices
        description: Raw housing price data
        columns:
          - name: id
            description: Unique identifier for each record
            tests:
              - unique
              - not_null
          - name: date
            description: Date of the housing price record
            tests:
              - not_null
          - name: region
            description: Region/city where the house is located
            tests:
              - not_null
          - name: price
            description: Price of the house in the local currency
            tests:
              - not_null
```

---

## Full schema.yml – raw\_location\_data

```yaml
      - name: raw_location_data
        description: Raw location reference data
        columns:
          - name: postcode
            description: Postal code
            tests:
              - unique
              - not_null
          - name: region
            description: Region/city name
            tests:
              - not_null
          - name: type
            description: Type of location
            tests:
              - not_null
```

---

## Silver Layer – Clean & Enriched

The Silver Layer is the **Enriched Zone**: It acts as a trusted source by defining structure, schema, and fixed data quality.  

- Key characteristics:
  
  - Each source is handled independently
  - Data is cleaned, normalized, and standardized
  - Quality fixes are layered in a single transformation pipeline
  - Each layer builds on the previous one towards a trusted source
  - Consistent naming conventions applied
  - Clear progression from raw to trusted data

- Examples:
  
  - Standardized housing price data with consistent formats
  - Currency values normalized to a single currency
  - Quality fixes layered in sequence:
    - Layer 1: Basic type casting and null handling
    - Layer 2: Business rule validation
    - Layer 3: Standardization and final checks
    - Result: Single trusted source table

Note: Joins between sources are strictly reserved for the Gold layer

---

## Schema Example – Silver Layer

* use`schema.yml` for cleaned models (e.g. `stg_` prefixed models).

* This example is extensive — it documents every column with tests and descriptions.

* In practice, you don't have to document everything:
  
  * Focus on columns that are non-obvious to others without domain knowledge.
  * For example, a column like `region` might not need documentation unless it's ambiguous.

* The example is split into three parts for readability across slides. 

------

## Full schema.yml – stg\_housing\_prices (Part 1)

```yaml
version: 2

models:
  - name: stg_housing_prices
    description: Staged housing prices with additional date dimensions
    columns:
      - name: id
        description: Unique identifier for each record
        tests:
          - unique
          - not_null
      - name: date
        description: Date of the housing price record
        tests:
          - not_null
      - name: region
        description: Region/city where the house is located
        tests:
          - not_null
```

---

## Full schema.yml – stg\_housing\_prices (Part 2)

```yaml
      - name: price
        description: Price of the house in the local currency
        tests:
          - not_null
      - name: year
        description: Year extracted from date
        tests:
          - not_null
      - name: month
        description: Month number (1-12) extracted from date
        tests:
          - not_null
          - accepted_values:
              values: [1,2,3,4,5,6,7,8,9,10,11,12]
      - name: day_of_week
        description: Day of week (0-6, where 0 is Sunday) extracted from date
        tests:
          - not_null
          - accepted_values:
              values: [0,1,2,3,4,5,6]
```

---

## Full schema.yml – stg_location_data (Part 3)

```yaml
  - name: stg_location_data
    description: Staged location reference data with standardized formatting
    columns:
      - name: postcode
        description: Postal code (primary key)
        tests:
          - unique
          - not_null
      - name: region
        description: Standardized region/city name in uppercase
        tests:
          - not_null
      - name: type
        description: Location type with proper capitalization
        tests:
          - not_null
```

---

---

## Building Silver Models (Hands-On)

* Run:

```bash
dbt run
```

* Confirm your new models `stg_housing_prices` and `stg_location_data` exist and function as expected. 
  1. Connect to the database: `psql -h localhost -U postgres -d dwh` 
  2. Then, view all tables: `\dt silver.*` 
  3. Query your model: `SELECT * FROM silver.stg_housing_prices LIMIT 5` 
  4. Exit psql: `\q`



---

## Run dbt Tests

* Now that your schema files are in place, it's time to validate your models.

* Run all tests defined in `schema.yml` using `dbt test`.
  
  * Executes all column-level tests (like `not_null`, `unique`, `accepted_values`).
  * Runs any custom tests you've added (We'll review these tomorrow!).
  * Gives you a detailed pass/fail overview in your terminal.

* These test names are auto-generated by dbt based on schema configuration.
  
  

Tip: Tests help catch problems early before they reach dashboards or reports.

---

## Sample dbt Test Output

```bash
12:11:37  1 of 23 START test accepted_values_stg_housing_prices_day_of_week__0__1__2__3__4__5__6  [RUN]
12:11:37  3 of 23 START test not_null_stg_housing_prices_date ............................ [RUN]
12:11:37  3 of 23 PASS not_null_stg_housing_prices_date .................................. [PASS in 0.11s]
12:11:38  22 of 23 START test unique_stg_housing_prices_id ............................... [RUN]
12:11:38  22 of 23 PASS unique_stg_housing_prices_id ..................................... [PASS in 0.06s]
```

* How to read test names:
  
  * `not_null_stg_housing_prices_id`
    
    * `not_null`: test type (built-in)
    * `stg_housing_prices`: model name
    * `id`: column being tested

* dbt automatically constructs these names using the schema file.

* Every line lists a) what dbt is testing, b) how long it took, c) pass/fail rating.

--- 

## After the Break: What's Next?

* Before we dive into **gold models**, let's have a quick recap: 
  
  * We ingested raw data into the **bronze layer**.
  * We cleaned and enriched it in the **silver layer**.
  * We've validated data with **automated tests**.

* The **gold layer**:
  
  * Builds high-value outputs for reporting or dashboards.
  * These are often called **data marts**.

* Reminder: **medallion architecture** separates:
  
  * **Bronze** = raw source data
  * **Silver** = cleaned, joined, validated
  * **Gold** = business logic, aggregates, metrics, KPIs

---

## Silver Model Overview

These two tables form the clean and standardized data foundation for the gold model.

| `stg_housing_prices` Columns  | `stg_location_data` Columns |
| ----------------------------- | --------------------------- |
| id (unique, not null)         | postcode (unique, not null) |
| date (not null)               | region (not null)           |
| region (not null)             | type (not null)             |
| price (not null)              |                             |
| year (not null)               |                             |
| month (1–12, not null)        |                             |
| day\_of\_week (0–6, not null) |                             |



---

## Designing a Gold Data Mart

Your goal is to build a **region-level housing price mart**. ` stg_housing_prices` has no postcode — only regions. So, we can't directly join the two tables.

### Alternative strategy:

1. Group `stg_location_data` by region and pivot `type` counts (e.g. number of URBAN vs RURAL locations).
2. Join this to `stg_housing_prices` on region.
3. Then aggregate housing prices per region + type split.

### Result:

You should now have a mart showing average price per region, with context on area composition (e.g. % urban); a useful summary without requiring postcode data.

---

## Gold Step 1: Move the Pivot to Gold

Where does your new grouped and pivoted location data belong? 

* This model belongs in the **gold zone** because it's:
  
  * Business-facing: It describes region composition.
  * Summarized: Region-level rather than row-level aggregates.
  * Enriched with derived columns: e.g. percentage urban.
  
  

---

## Gold Step 2: Pivot Location Types by Region

We'll begin by transforming `stg_location_data` into a per-region summary with type counts:

```sql
WITH type_counts AS (
  SELECT
    region,
    COUNT(*) FILTER (WHERE type = 'URBAN') AS urban_count,
    COUNT(*) FILTER (WHERE type = 'RURAL') AS rural_count,
    COUNT(*) AS total_locations
  FROM {{ ref('stg_location_data') }} GROUP BY region
)

SELECT
  region, urban_count,  rural_count,
  ROUND(urban_count * 1.0 / total_locations, 2) AS pct_urban
FROM type_counts
```

This prepares a normalized region → type breakdown.

---

## Gold Step 3: Final Gold Mart – SQL Join & Aggregate

Create the data mart using `nano models/gold/mart_housing_prices_breakdown.sql`:

```sql
WITH avg_prices AS (
  SELECT
    region,
    AVG(price) AS avg_price,
    COUNT(*) AS n_sales
  FROM {{ ref('stg_housing_prices') }} GROUP BY region
)

SELECT
  p.region, p.avg_price, p.n_sales,
  r.urban_count, r.rural_count,  r.pct_urban
FROM avg_prices p
LEFT JOIN {{ ref('region_type_composition') }} r
  ON p.region = r.region
```

* This is our gold model: high-value, aggregated, and explained.
* You can now visualize or explore this in downstream dashboards.

---

## Gold Model Schema Strategy

* Not every model needs a schema entry.

* You usually write `schema.yml` for:
  
  * Models that are **final outputs**, **shared with others**, or **tested**.
  * Tables that show up in dashboards or feed reporting layers.

* `schema.yml` outputs:
  
  * Column-level tests (like `not_null`, `unique`, etc.).
  * Documentation for interactive lineage and team onboarding.
  * Exposure in `dbt docs` and lineage graphs.

* Don't worry about writing complete descriptions now. Instead, focus on building meaningful tests and adding clarity. 

---

## Full schema.yml – mart\_housing\_prices\_breakdown

```yaml
version: 2

models:
  - name: mart_housing_prices_breakdown
    description: Region-level summary of housing prices with urban/rural composition
    columns:
      - name: region
        description: Region name
        tests:
          - not_null
      - name: avg_price
        description: Average housing price in the region
        tests:
          - not_null
      - name: n_sales
        description: Number of sales (rows) for that region
        tests:
          - not_null
      - name: urban_count
        description: Number of urban locations in the region
        tests:
          - not_null
      - name: rural_count
        description: Number of rural locations in the region
        tests:
          - not_null
      - name: pct_urban
        description: Share of locations that are urban (0–1)
        tests:
          - not_null
```

---

## Full schema.yml – region\_type\_composition

```yaml
  - name: region_type_composition
    description: Region-level breakdown of urban and rural location counts
    columns:
      - name: region
        description: Region name
        tests:
          - not_null
      - name: urban_count
        description: Number of urban locations in the region
        tests:
          - not_null
      - name: rural_count
        description: Number of rural locations in the region
        tests:
          - not_null
      - name: total_locations
        description: Total number of locations in the region
        tests:
          - not_null
      - name: pct_urban
        description: Share of locations that are urban (0–1)
        tests:
          - not_null
```

---

## Open the dbt Docs UI

Let's explore the documentation and lineage together!

1. Go to Docker Desktop.

2. Go to Containers & click dbt.

3. Click on exec.

4. Enter:

```bash
dbt docs generate
dbt docs serve --port 8081 --host 0.0.0.0
```

5. Then open this link in your browser:
   [http://localhost:8081

6. Click around and find out!

---

## Exploring dbt Docs

* The docs UI lets you:
  
  * View model information including name, SQL, materialization type, etc. 
  * Click into upstream and downstream dependencies.
  * See columns, descriptions, and test coverage.

* There is **no** full visual lineage graph in dbt Core - we'll find that in dbt cloud.
  
  * You can see **"depends on" / "referenced by"** sections per model.
<center>
<img src="/home/marp/app/dbt_cloud_dependency_graph.png" alt="DBT Cloud Dependency" width="600"/>
</center>


--- 

## Wrap-up & Docs

### What you've learned today:

* How to create and structure **models**.
* How to define and apply **schemas**.
* How to add **tests** for data quality.
* How to explore and use **dbt docs**.

### Tomorrow, you'll take a deeper dive into dbt 