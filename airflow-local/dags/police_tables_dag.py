# Standard library imports
import os
from datetime import datetime, timedelta

# Airflow imports
from airflow import DAG
from airflow.decorators import task
from airflow.models.dataset import Dataset
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.models import Variable 

# Local imports
from police_utils import (
    ListPoliceTables,
    ProcessPoliceTable,
    DocumentationOperator,
    UploadToDWHOperator,
    ListDWHTables,
    DescribeDWHTable,
    get_postgres_asset_uri
)
from dbt_utils import (
    DbtGenerateProfilesOperator,
    DbtDebugOperator,
    DbtRunOperator,
    DbtTestOperator,
    DbtSeedOperator,
    DEFAULT_DBT_DIR
)

# This DAG demonstrates how to use the custom Police Operators for exploring and processing police data.
# The main operators are:
#
# ListPoliceTables - Search CBS Open Data for police-related tables
#   Example: ListPoliceTables(task_id='list_tables', search_term='politie')
#
# ProcessPoliceTable - Download and process a specific table
#   Example: ProcessPoliceTable(task_id='process_table', table_name='table_name')
#
# UploadToDWHOperator - Load processed data into the data warehouse
#   Example: UploadToDWHOperator(task_id='upload', connection_id='dwh', xcom_task_id='process_table')
#
# Feel free to explore the code and experiment with different tables and configurations.
# The full documentation for each operator can be found in police_utils.py
#
# Note: This DAG uses .expand() which is an advanced Airflow concept for dynamic task generation.
# Don't worry if this part is unclear - you can skip those sections and focus on understanding
# the basic operator usage first!


# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


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
    
    def check_nuclear():
        return Variable.get("NUCLEAR", default_var=None) is not None

    # Add ShortCircuitOperator at the start
    check_nuclear_switch = ShortCircuitOperator(
        task_id='check_nuclear_switch',
        python_callable=check_nuclear,
    )
    
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
        search_term='politie'
    )

    # Example 1: Dynamic mapping - process all found tables 
    process_all_tables = ProcessPoliceTable.partial(
        task_id='process_all_tables',
    ).expand(
        table_data=list_tables.output
    )

    # Example 2: Direct instantiation - process a specific table
    process_specific_table = ProcessPoliceTable(
        task_id='process_budget_table',
        table_name='vertrouwen_in_mensen__recht_en_politiek_843',  # Replace with actual table name
    )

    # Set up dependencies - make everything dependent on the nuclear check
    [doc_list_tables, doc_process_table] >> check_nuclear_switch >> list_tables >> [process_all_tables, process_specific_table]

    @task(
        task_id="list_final_assets",
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

with DAG(
    'police_example',
    default_args=default_args,
    description='Process police-related tables from CBS Open Data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['cbs', 'police', 'day_four'],
) as dag:
    # Process individual election tables
    process_ep_1999 = ProcessPoliceTable(
        task_id='process_ep_1999',
        table_name='europees_parlement_landelijk__1999_4278',
        outlets=[Dataset(f"data/europees_parlement_landelijk__1999_4278.json")]
    )

    process_ep_1994 = ProcessPoliceTable(
        task_id='process_ep_1994', 
        table_name='europees_parlement_landelijk__1994_4279',
        outlets=[Dataset(f"data/europees_parlement_landelijk__1994_4279.json")]
    )

    process_ep_1989 = ProcessPoliceTable(
        task_id='process_ep_1989',
        table_name='europees_parlement_landelijk__1989_4280',
        outlets=[Dataset(f"data/europees_parlement_landelijk__1989_4280.json")]
    )

    process_ep_1984 = ProcessPoliceTable(
        task_id='process_ep_1984',
        table_name='europees_parlement_landelijk__1984_4281',
        outlets=[Dataset(f"data/europees_parlement_landelijk__1984_4281.json")]
    )

    process_ep_1979 = ProcessPoliceTable(
        task_id='process_ep_1979',
        table_name='europees_parlement_landelijk__1979_4282',
        outlets=[Dataset(f"data/europees_parlement_landelijk__1979_4282.json")]
    )

    process_ps_1999 = ProcessPoliceTable(
        task_id='process_ps_1999',
        table_name='provinciale_staten_landelijk__1999_4283',
        outlets=[Dataset(f"data/provinciale_staten_landelijk__1999_4283.json")]
    )

    process_ps_1995 = ProcessPoliceTable(
        task_id='process_ps_1995',
        table_name='provinciale_staten_landelijk__1995_4284',
        outlets=[Dataset(f"data/provinciale_staten_landelijk__1995_4284.json")]
    )

    # Group all election processing tasks
    election_tasks = [
        process_ep_1999,
        process_ep_1994,
        process_ep_1989,
        process_ep_1984,
        process_ep_1979,
        process_ps_1999,
        process_ps_1995
    ]

    # Create individual upload tasks for each election dataset
    upload_tasks = []
    for task in election_tasks:
        # Get the file path from the dataset URI
        file_path = task.outlets[0].uri
        upload_task = UploadToDWHOperator(
            task_id=f'upload_{task.task_id}_to_dwh',
            connection_id='dwh',
            file_path=file_path,
            inlets=task.outlets,  # Keep the dataset dependency,
            outlets=[Dataset(get_postgres_asset_uri(fp)) for fp in task.outlets]
        )
        upload_tasks.append(upload_task)

        # So assets are DAG to DAG dependencies, not task to task dependencies
        task >> upload_task 

    # List all tables in the data warehouse
    list_tables = ListDWHTables(
        task_id='list_dwh_tables',
        connection_id='dwh',
        schema='public'
    )

    # Describe specific EP 1989 table
    describe_ep_1989 = DescribeDWHTable(
        task_id='describe_ep_1989',
        connection_id='dwh',
        table_name='europees_parlement_landelijk__1989_4280',
        schema='public'
    )

    # Add dependencies
    for upload_task in upload_tasks:
        upload_task >> list_tables >> describe_ep_1989


with DAG(
    'police_example_dbt',
    default_args=default_args,
    description='Process police-related tables from CBS Open Data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['cbs', 'police', 'day_four'],
) as dag:
    
    # Create dbt profiles from Airflow connection
    generate_profiles = DbtGenerateProfilesOperator(
        task_id='generate_dbt_profiles',
        connection_id='dwh',  # Use the same connection as UploadToDWHOperator
    )

    # Run dbt debug to verify configuration
    dbt_debug = DbtDebugOperator(
        task_id='dbt_debug',
        config=True  # Added config flag to show all configuration info
    )
    generate_profiles >> dbt_debug
 
    # Run dbt models
    dbt_run = DbtRunOperator(
        task_id='dbt_run'
    )

    dbt_debug >> dbt_run
    
    # Run dbt tests
    dbt_test = DbtTestOperator(
        task_id='dbt_test',
        select='+tag:silver'
    )

    dbt_run >> dbt_test
