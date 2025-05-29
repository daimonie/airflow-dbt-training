# Standard library imports
from datetime import datetime, timedelta

# Airflow imports
from airflow import DAG
from airflow.decorators import task

# Local imports
from police_utils import ListDWHTables, DescribeDWHTable

# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'explore_dwh',
    default_args=default_args,
    description='Explore tables in the data warehouse',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['dwh', 'day_four'],
) as dag:
    
    # List all tables in the data warehouse
    list_tables = ListDWHTables(
        task_id='list_dwh_tables',
        connection_id='dwh',
        schema='public'  # Assuming we're using the public schema
    )

    @task
    def get_table_names(**context):
        """Get the list of tables from the previous task."""
        tables = context['task_instance'].xcom_pull(task_ids='list_dwh_tables')
        return tables or []

    @task
    def describe_table(table_name: str):
        """Describe a single table from the data warehouse."""
        return DescribeDWHTable(
            task_id=f'describe_table_{table_name}',
            connection_id='dwh',
            table_name=table_name,
            schema='public'  # Assuming we're using the public schema
        ).execute(context={})

    # Set up the dynamic mapping
    table_names = get_table_names()
    described_tables = describe_table.expand(table_name=table_names)

    # Set up task dependencies
    list_tables >> table_names >> described_tables 