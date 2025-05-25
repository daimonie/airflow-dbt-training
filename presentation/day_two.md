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

# Airflow + dbt Training Day
## PDF Guide
# Intro to dbt – Afternoon Session

---

## Introduction to dbt – Why This Matters

* What problem did we want to solve?

  * Like many teams, we had SQL transformations scattered across dashboards, scripts, and notebooks.
  * This made them hard to maintain, test, or understand.
  * We wanted a way to treat SQL more like code — with dependencies, version control, and a clear structure.

---

## Introduction to dbt – What It Is

* What problem does dbt solve?

  * In many analytics workflows, SQL transformations are scattered across BI tools, spreadsheets, notebooks, and pipelines — making them hard to version, test, and collaborate on.
  * dbt solves this by turning SQL into a software development workflow.
* What is dbt? A transformation tool for analytics engineers.
* Emphasize: dbt is SQL-first, code-based, version-controlled, and testing-focused.

---

## Use Cases dbt Helps With

* Building clean, modular data pipelines in SQL
* Ensuring transformations are tested and trustworthy
* Making it easier for teams to collaborate on data code
* Automating documentation and dependency tracking
* Creating reliable data marts that feed dashboards
* Supporting analytics engineering as a practice

---

## dbt Compared to Other Tools – Common Alternatives

* **Using views in a database**:

  * Fast to set up, but hard to version or test.
  * No built-in dependency tracking or documentation.
* **Scheduled scripts or procedures**:

  * Common in legacy pipelines.
  * Often scattered, untested, and hard to debug or extend.
* **Manually wiring Airflow DAGs**:

  * Powerful but verbose.
  * Low-level and not focused on data modeling or testing.

---

## dbt Compared to Other Tools – How dbt Helps

* **How dbt improves things**:

  * Treats SQL like code: modular, version-controlled, tested.
  * Builds a workflow automatically inside dbt using `ref()` to determine dependencies.
  * Makes testing, documentation, and lineage part of the workflow.

---

## Models (SQL files)

* In dbt, each model is a `.sql` file that defines a transformation using a SELECT statement.
* dbt turns these into views or tables in your data warehouse.
* Keeps logic clean and modular — one transformation per file.

---

## Ref and Dependency Graph

* `ref()` lets you link one model to another in dbt.
* This builds a dependency graph automatically.
* dbt uses the graph to determine the correct run order.
* You get a workflow without writing orchestration code.

---

## Materializations

* Materializations define how dbt creates the output for each model.
* Options include:

  * `view`: re-runs every time, fast but temporary
  * `table`: persistent snapshot of the result
  * `incremental`: only update new data on each run
* You choose the materialization per model.

---

## Sources and Seeds

* **Sources** represent external data already in your warehouse.

  * Lets you declare where your raw tables live.
  * Adds lineage and testing for upstream data.
* **Seeds** are CSV files that dbt loads as tables.

  * Great for reference data or small lookup tables.

---

## Testing

* dbt allows you to write **tests** as first-class citizens.

  * Built-in tests: `not_null`, `unique`, `accepted_values`, `relationships`
  * Custom tests: SQL queries that should return zero rows.
  * Catch issues early and keep data quality in check.

---

## Documentation and Lineage

* dbt can generate interactive docs from your project.

  * Shows columns, descriptions, tests, and relationships.
* Lineage graph helps you understand dependencies across models.

  * Run with `dbt docs generate` and `dbt docs serve`

---

## Jinja in dbt (With Example)

* Jinja lets you use logic inside SQL — loops, variables, conditions.
* Example usage inside a model:

```sql
SELECT *
FROM {{ source('weather', 'daily') }}
WHERE region = '{{ var("region", "north") }}'
```

* Useful for avoiding repetition and introducing templating.

---

## Medallion Architecture – The Concept

* Medallion Architecture is a pattern for organizing data workflows using three layers:

  * **Bronze**: raw, ingested data
  * **Silver**: cleaned and joined data
  * **Gold**: business-level aggregates and facts
* Encourages clear separation of concerns and reproducibility.
* Gaining traction in the industry — highlighted in the recent O'Reilly book by Piet-Hein Strengholt, former Microsoft NL CDO and now leading at Nationale Nederlanden.

---

## Bronze Layer – Raw Ingestion

* This is your **Landing Zone**
* Ingested data, minimal transformation
* Key goal: capture source as-is with metadata (e.g. timestamps)
* Examples:

  * Raw CSV load from CBS
  * API snapshots

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

* `schema.yml` defines sources and tests for raw data
* Example structure:

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

* Matches the **Enriched Zone**
* Data is cleaned, normalized, and made more usable
* Joins across sources happen here
* Examples:

  * Joined housing price + postcode table
  * Currency exchange cleaned and unified

---

## Schema Example – Silver Layer

* `schema.yml` for cleaned models (e.g. `stg_` prefixed models)
* This example is very extensive — it documents every column with tests and descriptions.
* In practice, you don't have to document everything:

  * Focus on columns that are non-obvious or useful to others without domain knowledge.
  * For example, a column like `region` might not need documentation unless it's ambiguous.
* We've split the example into three parts to make it readable on slides.

---

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

## Full schema.yml – stg_location_data

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
````

---

## Creating Silver Models (Hands-On)

* Run the following:

```bash
dbt run
```

* Confirm the new models `stg_housing_prices` and `stg_location_data` exist and are correct

---

## Schema Example – Silver Layer

* `schema.yml` for cleaned models (e.g. `stg_` prefixed models)
* Tests and documentation now apply to enriched fields

```yaml
version: 2
models:
  - name: stg_housing_prices
    columns:
      - name: date
        tests: [not_null]
      - name: year
        description: "Year extracted from date"
```

---

## Run dbt Tests

* Now that your schema files are in place, it's time to validate your models.
* Run all tests defined in `schema.yml` using `dbt test`

* This command will:

  * Execute all column-level tests (like `not_null`, `unique`, `accepted_values`)
  * Run any custom tests you've added
  * Give you a detailed pass/fail overview in your terminal

* These test names are auto-generated by dbt based on your schema configuration.

* Example: `not_null_stg_housing_prices_id`

  * `not_null`: the test type being applied
  * `stg_housing_prices`: the model name (filename without `.sql`)
  * `id`: the column the test is applied to

* Tip: Tests help catch problems early before they reach dashboards or reports.

---

## Sample dbt Test Output

```bash
12:11:37  1 of 23 START test accepted_values_stg_housing_prices_day_of_week__0__1__2__3__4__5__6  [RUN]
12:11:37  3 of 23 START test not_null_stg_housing_prices_date ............................ [RUN]
12:11:37  3 of 23 PASS not_null_stg_housing_prices_date .................................. [PASS in 0.11s]
12:11:38  22 of 23 START test unique_stg_housing_prices_id ............................... [RUN]
12:11:38  22 of 23 PASS unique_stg_housing_prices_id ..................................... [PASS in 0.06s]
```

* How to read the test name:

  * `not_null_stg_housing_prices_id`

    * `not_null`: test type (built-in)
    * `stg_housing_prices`: model name
    * `id`: column being tested
* These names are automatically constructed by dbt based on your schema file.
* Every line tells you what dbt is testing, how long it took, and whether it passed or failed.

--- 

## After the Break: What's Next?

* Before we dive into gold models, let's recap where we are:

  * We ingested raw data into the **bronze layer**.
  * We cleaned and enriched it in the **silver layer**.
  * We've validated everything with **automated tests**.

* Now it's time for the **gold layer**:

  * This is where we build high-value outputs for reporting or dashboards.
  * These are often called **data marts**.

* Reminder: the **medallion architecture** separates:

  * **Bronze** = raw source data
  * **Silver** = cleaned, joined, validated
  * **Gold** = business logic, aggregates, metrics, KPIs

---

## Silver Models Overview

| `stg_housing_prices` Columns  | `stg_location_data` Columns |
| ----------------------------- | --------------------------- |
| id (unique, not null)         | postcode (unique, not null) |
| date (not null)               | region (not null)           |
| region (not null)             | type (not null)             |
| price (not null)              |                             |
| year (not null)               |                             |
| month (1–12, not null)        |                             |
| day\_of\_week (0–6, not null) |                             |

* These two tables form the cleaned and standardized foundation for the gold model.

---

## Designing a Gold Data Mart

* Our goal is to build a **region-level housing price mart**.
* Problem: `stg_housing_prices` has no postcode — only region.
* So, we can't directly join the two tables.

### Alternative strategy:

* Group `stg_location_data` by region and pivot `type` counts (e.g. number of URBAN vs RURAL locations).
* Join this to `stg_housing_prices` on region.
* Then aggregate housing prices per region + type split.

### Result:

* A mart showing average price per region, with context on area composition (e.g. % urban).
* This gives us a useful summary without requiring postcode data.

---

## Gold Step 1: Move the Pivot to Gold

* This model belongs in the **gold zone** because it's:

  * Business-facing: it helps describe region composition.
  * Summarized: not row-level, but region-level aggregates.
  * Enriched with derived columns: e.g. percentage urban.

* Where to save it:

```bash
nano models/gold/region_type_composition.sql
```

* Save the output as a **view** (default materialization).
* Now we can build on top of this in later models.

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

* This prepares a normalized region → type breakdown.
* Next step: join this with housing prices.

---

## Gold Step 3: Final Gold Mart – SQL Join & Aggregate

Now we create the data mart using `nano models/gold/mart_housing_prices_breakdown.sql`:

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
  * Tables that show up in dashboards, or feed reporting layers.

* What a `schema.yml` brings:

  * Column-level tests (like `not_null`, `unique`, etc.)
  * Documentation for interactive lineage and team onboarding
  * Exposure in `dbt docs` and lineage graphs

* Don't worry about writing complete descriptions now.

  * Focus on meaningful tests and clarity where needed.

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

* Let's explore the documentation and lineage together!
* Run this in your terminal (if you haven't already):

```bash
dbt docs generate
dbt docs serve --port 8081 --host 0.0.0.0
```

* Then open this link in your browser:
  [http://localhost:8081](http://localhost:8081)

---

## Exploring the Lineage Graph

* The docs UI lets you:

  * View model information: name, SQL, materialization type
  * Click into upstream and downstream dependencies
  * See columns, descriptions, and test coverage

* There is no full visual lineage graph in dbt Core.

  * You can see **"depends on" / "referenced by"** sections per model.
  * A full **interactive lineage graph** is only available in **dbt Cloud**, which we'll explore tomorrow.

--- 
## Wrap-up & Docs

### What you've learned today:

* How to create and structure **models**
* How to define and apply **schemas**
* How to add **tests** for data quality
* How to explore and use **dbt docs**

### Tomorrow, you'll learn:

* How to track model usage with **exposures**
* How to optimize workflows in **dbt Cloud**
* How to define efficient **materializations** (like `incremental`)
* How to use **macros** and Jinja for automation and reuse

We'll also:

* Link models to dashboards using exposures
* Set up scheduled jobs in dbt Cloud
* Walk through building more dynamic, production-ready projects
