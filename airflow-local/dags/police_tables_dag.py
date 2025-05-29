# Standard library imports
import os
from datetime import datetime, timedelta

# Airflow imports
from airflow import DAG
from airflow.decorators import task
from airflow.models.dataset import Dataset
from airflow.operators.bash import BashOperator

# Local imports
from police_utils import (
    ListPoliceTables,
    ProcessPoliceTable,
    DocumentationOperator,
    UploadToDWHOperator
)

# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create dataset assets for each file in data/
data_dir = "data"
datasets = []

if os.path.exists(data_dir):
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            dataset = Dataset(os.path.join(data_dir, filename))
            globals()[f"dataset_{filename[:-5]}"] = dataset
            datasets.append(dataset)

with DAG("refresh_airflow", tags=['day_four'],):
    reserialize = BashOperator(
        task_id="reserialize",
        bash_command="airflow dags reserialize"
    )

with DAG(
    'police_tables_processing',
    default_args=default_args,
    description='Process police-related tables from CBS Open Data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['cbs', 'police', 'day_four'],
) as dag:
    
    # Get documentation for our custom operators
    doc_list_tables = DocumentationOperator(
        task_id='doc_list_tables',
        object_name='ListPoliceTables'
    )

    doc_process_table = DocumentationOperator(
        task_id='doc_process_table', 
        object_name='ProcessPoliceTable'
    )

    # List all police-related tables
    list_tables = ListPoliceTables(
        task_id='list_police_tables',
        search_term='politie',
        limit=10
    )

    # Example 1: Dynamic mapping - process all found tables 
    process_all_tables = ProcessPoliceTable.partial(
        task_id='process_all_tables',
        outlets=datasets  # Use our pre-defined datasets
    ).expand(
        table_data=list_tables.output
    )

    # Example 2: Direct instantiation - process a specific table
    process_specific_table = ProcessPoliceTable(
        task_id='process_budget_table',
        table_name='vertrouwen_in_mensen__recht_en_politiek_843',  # Replace with actual table name
    )

    # Set up dependencies
    [doc_list_tables, doc_process_table] >> list_tables >> [process_all_tables, process_specific_table]

    @task(
        task_id="list_final_assets",
        outlets=datasets  # Also mark this task as producing these datasets
    )
    def list_final_assets(): 
        all_assets = []
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    print(f"Found asset: data/{filename}")
                    all_assets.append(f"data/{filename}")
        else:
            print("No assets found")

        return all_assets

    final_assets = list_final_assets()
    process_all_tables >> final_assets

    # Upload the final assets to the data warehouse
    upload_to_dwh = UploadToDWHOperator(
        task_id='upload_to_dwh',
        connection_id='dwh',  # You'll need to configure this connection in Airflow
        xcom_task_id='list_final_assets'  # Get file paths from the list_final_assets task
    )

    final_assets >> upload_to_dwh

    