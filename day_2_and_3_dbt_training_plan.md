# Day 2 — Deepening Airflow & dbt Kickoff (09:30–16:30)

## Morning Block 1 (09:30–11:00): Airflow Recap + Advanced DAGs + Extra Features
1. **Recap: Core Airflow Concepts**
   - Briefly revisit DAG structure, operators, dependencies, and how Airflow executes tasks.
   - Show how Jinja templating and `params` can help make DAGs more reusable.
   - Introduce concepts of user roles and how to manage them in Airflow.
   - Mention Assets (new in Airflow 2.8+): a feature for declaring task outputs that enables better DAG lineage and observability. Briefly introduce how this parallels dbt's concept of Assets (models, seeds, snapshots) that form a dependency graph in dbt Cloud.
   - Optional: Mention REST API and CLI usage for triggering/running tasks programmatically.
2. **Live Demo DAG: Dissecting a Real-World Pattern**
   - Step through the more advanced DAG from Day 1 (BranchPythonOperator, TriggerDagRunOperator).
   - Talk through the logic, use cases, and how it connects to orchestration in a real job.
3. **Hands-on: Build Your Own Branching DAG**
   - Guided exercise recreating the logic shown in the demo.
   - Focus on turning logic into readable and maintainable DAG structure.

## Morning Block 2 (11:15–12:30): dbt Fundamentals, Setup & First Model
4. **Intro to dbt: Transform, not Load**
   - Why dbt? A tool for SQL-based transformations with structure and testing.
5. **Medallion Architecture: Bronze, Silver, Gold**
   - Conceptual framing of data layers; how these align with Landing, Enriched, and Curated.
6. **Installing dbt in the Airflow Container**
   - Step-by-step: `profiles.yml`, Docker terminal, schema setup.
7. **Data Context: Housing Prices + Location**
   - Introduce housing + location dataset to work with.
   - Show example fields (e.g. postcode, price index, region).
8. **First Model: Bronze → Silver**
   - Create one clean staging model using `ref()`.
   - Confirm schema and inspect intermediate output.

## Lunch (12:30–13:30)

## Afternoon Block 1 (13:30–15:00): Expanding Your dbt Project
9. **Building Out Silver → Gold**
   - Extend your model from staging to gold-level mart tables.
   - Add useful aggregations, filters, or joins.
10. **Generating dbt Docs**
   - Run `dbt docs generate` and inspect lineage/output locally.
   - Show the difference if you had Cloud — scheduler, UI, lineage explorer.

## Afternoon Block 2 (15:15–16:30): Hands-On Expansion
11. **Group Work: Model More Sources**
   - Build models for the rest of the housing data (e.g. postcodes, demographics).
12. **Add Tests**
   - Basic data quality checks: not null, accepted values.
13. **Overflow Topics (if time allows):**
   - Dev vs Prod setup patterns
     - Show how you can structure dbt to write to `{user}_schema` in dev, and shared schema in production
     - This helps prevent accidental overwrites and supports team-based workflows
   - Introduce dbt Snapshots: a feature for tracking slowly changing dimensions (SCDs) over time using hash-based diffs. Useful for historical records like housing prices, ownership changes, or contract evolution.

---

# Day 3 — Advanced dbt Concepts (09:30–16:30)

## Morning Block 1 (09:30–11:00): dbt Cloud Showcase or Deepening Core Features
1. **dbt Cloud Showcase (if not covered on Day 2)**
   - Start the day by showcasing the same housing dataset project, now hosted on dbt Cloud + BigQuery.
   - Walk through lineage, docs, scheduler, test results, and version control integration.
2. **Recap & Check-in**
   - Share learnings and blockers from Day 2.
3. **Exposures: From Data to Dashboard**
   - Show how to define downstream dependencies and document them.
   - Use SQL + Jinja to define quality gates tailored to your data.

## Morning Block 2 (11:15–12:30): Incremental Models
4. **Incremental Logic: Performance Patterns**
   - Difference from full-refresh, partitioning, and `is_incremental()` logic.
5. **Hands-On: Build Your First Incremental Model**
   - Use a timestamp-based housing dataset as source.

## Lunch (12:30–13:30)

## Afternoon Block 1 (13:30–15:00): Templates, Reuse, and Deeper Modeling
6. **Expanding Your Gold Models Further**
   - Add more complex business logic to your gold models, including multi-source joins, window functions, or geospatial grouping.
   - Reinforce dbt model structure and build confidence in gold-layer logic.
   - **Hands-on Challenge:** Create a gold model that calculates average housing price trends by region. Include logic for filtering outliers, grouping by time or geography, and joining to region metadata. Use `ref()` and Jinja where appropriate to maintain a clean and modular structure.
7. **Jinja in dbt: DRY Patterns**
   - How loops and conditionals help simplify boilerplate.
8. **Refactoring to Reusable Macros**
   - Turn common logic into a project macro.
9. **Packaging and Sharing Logic**
   - How to structure internal dbt packages for reuse.

## Afternoon Block 2 (15:15–16:30): Open Lab & Guided Work
10. **Guided Lab: Extend or Polish Your Pipelines**
   - Choose your focus: more tests, exposures, modularizing, or adding another data source.
11. **Overflow Options (as needed):**
   - Adding snapshot models (to track slowly changing data over time using dbt's built-in snapshot feature)
   - Advanced documentation strategies
   - Collaborating across teams in dbt projects
   - **dbt Cloud Showcase (Pre-configured Demo Only):**
     - Because dbt Cloud cannot connect to local-only databases, we’ll use a pre-configured demo project connected to BigQuery.
     - This will demonstrate features like the lineage explorer, scheduled runs, documentation, and test outputs in a real hosted environment.
     - No hands-on account setup required; just follow along.
