# Dockerfile
FROM apache/airflow:2.8.1-python3.10

USER root

# Install docker CLI and dbt dependencies
RUN apt-get update && apt-get install -y docker.io

USER airflow
RUN pip install --no-cache-dir dbt-core dbt-postgres
RUN pip install --no-cache-dir cbsodata psycopg2-binary>=2.9.9 scikit-learn
 