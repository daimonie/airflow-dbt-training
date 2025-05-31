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

# Airflow and DBT (TEST conversion)
## Day one: Airflow

### WIFI 2f4o9r1eAC [console.cloud.google.com](http://console.cloud.google.com)

### Josko de Boer

---

# Introductions

- Polite Greeting
- Your Name  
- Relevant Personal Link
- Clear Expectations

---

# What is Airflow?

Apache Airflow is an open-source workflow management platform for creation, scheduling, & management of data-engineering pipelines

- Implement programs from any language
- Workflows are written in Python
- Implements Workflows as Directed Acyclic Graphs (DAGs)
- Workflows are accessed via code, command line, or web-interface/REST API

---

# What is dbt?

Data Build Tool (dbt) is a development framework combining modular SQL with software engineering best-practices to enable reliable and fast data transformation

- Write custom business logic using SQL
- Build data pipelines
- Automate data quality testing
- Deliver data with documentation side-by-side with code

---

# Day one: The plan

**10.00** Airflow Basics:
- Use case
- Airflow in a nutshell

**10.45** Short Break

**11.00** Hands-on: Building a basic DAG

**12.00** Lunch I'm sure

**13.00** Airflow: Let's dive deeper
- Internal architecture
- XCOM
- DAGs
- Sensors

**14.00** Short Break

**14.15** Custom Operator: Python Code

**16.00** Airflow Use Case: Centralized Pipelines

**16.30** End

---

# Use-case: Transparent pipelines with Airflow

We had a large, unorganized dataset of questionable quality. We were asked to fix the dataset to improve quality and enable the extraction of credible market insights for the company. We identified goals including:

- Extracting data from the central data team (AWS Redshift)
- Deduplication
- Cleaning
- Filling in missing data using business logic
- Filling in missing data or enhancing data using Machine Learning models
- Loading the final enhanced dataset into a PostgreSQL database for the webapp

How could we create a clear, transparent, and manageable pipeline? We chose Airflow

---

# Use-case: Transparent pipelines with Airflow (2)

Airflow allowed us to:

- Build transparency into the workflow
- Optimize the development workflow
- Easily re-run failed Tasks
- Deliver insight into when Tasks ran, for how long, etc
- Integrate services as needed (Python, SQL, Redshift, Kubernetes, Lambdas)

And because Airflow is Python, it was fairly easy to get started on migrating our pipeline to a clean setup with CI/CD, including unit tests.

---

# Airflow in a nutshell

Apache Airflow is an open-source workflow management platform for creation, scheduling, & management of data-engineering pipelines

- DAGs
- Tasks
- UI features
- Jinja templating

---

# What are DAGs?

**Directed Acyclic Graph (DAG)**

A one-directional flow-chart of tasks

- Tasks
- Task dependencies  
- Task details (Name, start date, owner, etc.)

---

# What are Tasks?

Tasks are the basic executable unit in Airflow.

Tasks are organized into DAGs, with upstream and downstream dependencies (the flowchart / DAG) and are executable.

There are three types:

- **Operators**: pre-defined, reusable Tasks
- **Sensors**: a Task type that waits until a condition is met before executing
- **TaskFlow decorators**: custom python code (@task)

---

# Operators: Pre-defined, reusable Tasks

- **BashOperator**: Executes a Bash script
- **PythonOperator**: Executes python code
- **EmailOperator**: Sends an email
- **KubernetesPodOperator**: Interacts with Kubernetes Pods

And many, many more. Some are also ecosystem dependent.

---

# Sensors: They sense things.

Sensors are Operators designed to execute when triggered by an event. Sensors can be time-based, wait for a file, or an external event, but they wait for a condition to be met and then execute so downstream Tasks can run.

Examples:

- **DayTimeSensor**: Waits for specific day and time
- **ExternalTaskSensor**: Triggers when another Task finishes
- **SQLSensor**: Waits for data to arrive

Sensors have one flaw, and we will discuss that this afternoon.

---

# Taskflow decorators - Creating Tasks with API

TaskFlow decorators such as `@task` are programming patterns that add functionality to an object. In this case, they turn functions into tasks with an ID, facilitate passing data between Tasks, and define dependencies. 

Decorators create similar functionality to and are interoperable with classical Operators, including PythonOperator.

TaskFlow is newer and therefore preferable over building the same functionality in PythonOperator.

---

# UI features

The Airflow UI offers a feature-rich interface for:

- Monitoring Workflows and Tasks
- Visualization for Workflows
- Visualizing connections
- These are also a one-stop for auth information for DAGs and Tasks
- Inspect DAGs and code from the UI (easier debugging)
- One-stop for Gantt charts, logs, timing, re-running, etc.

---

# Jinja Templating

Jinja is a lightweight templating engine for Python that embeds variables, logic, and control structures to dynamically generate text. It enables flexible configuration and parameterization, especially useful for defining dynamic content like SQL queries or configuration files.

Jinja improves DAGs by dynamically injecting task parameters, SQL code, and runtime values (like execution date) at runtime. This improves reusability, reduces hardcoding, and supports complex automation logic across time-based data pipelines.

---

# Airflow use-cases: Why?

- **Schedule workflows**: Automates recurring tasks like daily data jobs or reports.
- **Visual DAGs**: Clear, graphical view of task dependencies and execution status.
- **Modular Python code**: Workflows are written in Python, making them readable and reusable. Also easier to use than Infrastructure as Code variants like AWS step functions.
- **Agnostic**: Airflow is an Apache tool and can be used locally or with any cloud platform.
- **Handles failures**: Built-in retry, alerting, and logging for robust pipelines.
- **Track and debug**: Easy to inspect past runs, logs, and task outputs.
- **Extensible**: Supports plugins, custom operators, and integrates with many tools.
- **Scalable**: Run small local jobs or scale out with distributed executors (Celery, Kubernetes).
- **Templating & parameters**: Dynamically generate SQL, API calls, or filenames with runtime context.

---

# Morning exercise

Let's get started with Airflow! On the laptops, you'll find that Docker, WSL and Airflow are installed. Our first order of business:

- Open Docker and run the container for Airflow.

This is the equivalent of a fresh install — the UI is there, but we haven't created any DAGs yet.

**Let's create a DAG**

---

# Airflow: Let's dive deeper

- Internal Architecture
- XCom
- Dynamic DAGs
- DAG Dependencies
- DAGs with logic

---

# Airflow Architecture

- **Scheduler**: Triggers scheduled Workflows and submits tasks to the Executor.
- **Executor**: a configuration within the scheduler (not a separate component) determining how tasks are run (e.g., SequentialExecutor, LocalExecutor, CeleryExecutor, etc.).
- **DAG Processor**: Parses DAG files and serializes them into the metadata database.
- **Webserver**: Provides a UI to inspect, trigger, and debug DAGs and tasks.
- **DAG Folder**: Contains DAG files; the scheduler reads this to determine what to run and when.
- **Metadata Database**: Stores the state of workflows and tasks. Required for Airflow to function properly.

---

# Execution in Airflow

Scheduler triggers Task instances based on:

- DAG schedule
- Task dependencies
- Execution state (e.g., success/failure)

Each Task run needs one slot (available Task execution "seat" on a worker)

Total slots = parallelism limit (per worker and globally)

If no slots are free:
- Tasks are queued until a slot is available
- Sensors can block slots, wasting resources, unless they are deferrable operators

---

# XCOM: Cross-communication

**Use case**: Task 1 is uploading a file, after which, Task 2 must use that file. Both Tasks are executed asynchronously, but in the dependency order specified. How does Task 1 communicate the file path to Task 2?

XCOM is your answer. It simplifies passing messages between Tasks, but is specifically for small amounts of data.

For large amounts of data, cache it and pass that location onward instead.

---

# Dynamic DAGs: We're writing Python, aren't we?

DAGs generated with Python code are dynamic. When used with care, dynamic DAGs can simplify code and add real functionality. When used without care, they add amazing complexity and confusion.

---

# DAG dependencies

DAGs are flowcharts but sometimes you want to flowchart your flowcharts.

DAG-to-DAG dependencies are defined by either Triggering or Waiting:

- **TriggerDagRunOperator**: Start another DAG
- **ExternalTaskSensor**: Wait for a Task (likely the end of a different DAG)

**Warning**: This is a loosely-coupled dependency that can turn your nice new tool for transparency and visualization into a nightmare. Use with care and don't nest too deeply.

---

# Logical DAGs: When there are different options

`@task.branch` (BranchPythonOperator) uses if logic to select flowchart Tasks, turning a DAG into a logic tool.

---

# The problem with sensors

- A sensor waits for e.g. 2 hours.
- It occupies a slot for that time.
- It's blocking a slot for that time.

**Solution**: Use a Deferrable Operator to free the slot during the wait.

- Deferrable Operators use Triggerer, which waits for events in the background, and, when the condition is met, resumes the Task and uses the slot.
- Triggerer requires an additional lightweight process to be run alongside Airflow, which is why it isn't enabled by default.

---

# Custom Operators: Python

Let's write our own tasks using the `@task` decorator. Write a Python function to:

- Import the Iris dataset and store it locally.
- Define the mean of each feature per species
- Show correlation between petal length and petal width  
- Define global mean vector (average flower)

The Iris dataset is one of the most well-known beginner datasets in machine learning. It contains 150 samples of 3 iris species with 4 numeric features (sepal/petal length/width).

---

# Using @task

We can now easily add the `@task` decorator to turn our Functions into Tasks.

- How would you create the DAG from here?

---

# Building DAGs: Intuitive Python (but only if you're dutch)

The zen of python, a Poem about python: There should be one-- and preferably only one --obvious way to do it. Although that way may not be obvious at first unless you're Dutch.

- Why does this code work? Does it?
- XCom can be formulated to just look like native python passing variables

---

# A long time ago in a company far away

Disjointed ETLs: Ingestion and Transformation were handled in 10+ tools

- Ingestion could be using Kubernetes Pods, cronjobs, Pentaho, etc
- Transformation could be in Looker, BigQuery, Scheduled Queries, etc.
- Automations were run from local computers

**The plan**: Move to Airflow.

---

# Standardisation: What were we doing?

When we took inventory, we were facing the following challenges:

- **Ingestion**: A Kubernetes Pod configured with our own Importer Library.
- **Transformation**: SQL statements that either wrote table-to-table or table-to-view.
  - Needed scheduling and dependency.
- **Custom Pods**: A few special cases, such as A/B testing, machine learning and recommender systems

So…

---

# The Age of Airflow

- We wrote a new Operator/Task: **The Importer**
  - Configured our importer object and retrieved credentials to authenticate and ingest data

- We wrote a small library: **sql-transformation-pods**
  - Parsed yaml files with timing and dependencies (grouped in folders) into DAGs and Tasks

- We generalized for other use-cases: A pre-configured GKEPodOperator that allowed us to call for a specific container.

**And there we had it**: The New Grand Unified Data Platform Tool.

With Airflow, we moved ingestion and transformation from 10 tools to 1, created data visualizations for all pipelines, and centralized credentials and monitoring.

---

# The Age of Airflow

Amusingly, we were using yaml files with SQL statements, dependencies, sometimes unit tests, timing, etc?

**Sounds like the data build tool**

---

# User Management: Exercise 1

Let's examine users.

a. Navigate to http://localhost:8080 (your airflow install)
b. Login as the admin user (Changed this around - use admin/admin)
c. From the top menu, Security -> List Users
   - Which users are listed?
   - What roles do they have?

**CLI**: `airflow users list`

---

# User Management: Exercise 2

Let's examine built-in roles

a. Go to Security, then List Roles
b. Click on any role name to inspect what permissions it includes
   - Which role would you give to a dev?
   - Which role for a stakeholder?
   - What about your Product Owner?

---

# User Management: Exercise 3

Let's create a user.

a. Go back to Security, then List Roles
   i. Create a Role `product_owner` and set the following rights:
      1. menu_access on DAGs, menu_access on DAG Runs, menu_access on Task Instances
      2. Can_read on DAGs, can_read on DAG Runs, can_read on Task Instances
      3. Can_read on DAG Code
      4. Don't forget menu access on Browse and can read on Website!

b. Go back to Security, then List Users
   i. Create the product_owner user. See the "OID" by the email?
   ii. Assign the product_owner role we just created

c. Relog as the product_owner and see what you can do

---

# DAG Versioning - how does Airflow know what changed?

**Short answer**: modified time of the DAG file

- Keep all versions in the DAG Folder - avoid renaming files
- DAG ID stays the same - airflow updates code on file change
- **Best practice**: Use git versioning outside airflow.
  - This means code versioning (like git) happens outside of airflow
  - Your CI/CD pipeline will test your code, then deploy it by syncing your DAG folder to airflow server

---

# Airflow Variables

So you want to store some information, like "internal_team_url":

- Variables store runtime configuration values outside of the DAG code.
- Use them for:
  - Toggling features or tests
  - Small secrets - but real secrets go to Connections (next slide)
  - Variables are shared constants across DAGs

- Set variables in the UI: Admin -> Variables
- Accessed in code

---

# Notifications - do we need Email, or Teams?

We didn't configure this locally, but:

- Airflow can send alerts via:
  - Email
  - Teams (more custom)

**Simple Idea**
- Add recipients in variables
- Add teams config, including a channel
- Configure to either send it at the end of a workflow or on failure
  - Airflow provides on_failure_callback, and similar success and retry.
  - Requires python function to call when there is an issue.

---

# Connections

Airflow also provides tooling to store credentials and parameters.

- These can be used by Operators to authenticate and access services
- Define them once (in airflow), re-use them across DAGs
- Prevents hardcoding secrets or host info inside the DAGs themselves.

---

# Connections: where are they used?

Anything you want to connect to:

- Databases (Postgres, MySQL, BigQuery)
- Cloud storage and services
- APIs and other services
- Orchestration tools like dbt, spark, etc

---

# Let's create one!

We'll now create a connection we will re-use later.

- Go to Airflow UI, admin, connections, click the "+"
- Choose a Connection ID: `dwh_postgres`
- Set Connection Type to Postgres
- Fill in the fields:
  - Host: dwh
  - Schema: dwh
  - Login: airflow
  - Password: airflow
  - Port: 5432

Save this connection

---

# Custom Connection Integration

We will use this connection so DBT can connect to Postgres.

But it's not standard. Instead, I will provide the custom DbtConnectionOperator that reads this Connection and configures DBT automatically.

**How?**
- You can read connection info when creating the DAG (from python)
- This operator:
  - Reads the airflow connection info from the connection id you provide
  - Dynamically creates configuration for dbt
  - Can be reused in any DAG

It matters because it avoids hardcoding and reduces setup time.

---

# Airflow - what you know

We've covered:

- Building, scheduling and monitoring DAGs
- Connect to databases and services securely using Connections
- Track and visualize data lineage with Assets
- Assign and access roles, User Management via the UI
- Adding alerts, variables and custom logic using Python
- Using the UI to manage pipelines

---

# How to install locally?

- Get rid of your windows
- Download Docker Desktop https://www.docker.com/products/docker-desktop/
  - When asked for user - use the gmail we made earlier to interact with composer
  - IF Windows administrator is required: xm992#nz

- Make a folder in ~ Documents:
- Add docker-compose.yaml
- https://pastebin.com/QLRbgYMq

**Running docker compose to run airflow**

---

# data build tool (dbt)

They will get angry if you capitalize it. It's in the certification.

--- 