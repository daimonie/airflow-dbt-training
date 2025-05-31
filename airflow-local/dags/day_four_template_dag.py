# Give them this exact template to copy/paste/modify
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from police_utils import ListPoliceTables, ProcessPoliceTable, UploadToDWHOperator

# CHANGE THESE VALUES ONLY:
SEARCH_TERM = "politie"  # ← Change this
TABLE_NAMES = [          # ← Add your table names here
    "table_name_1",
    "table_name_2",
]

# DON'T CHANGE BELOW THIS LINE
with DAG(
    'your_dag_name_here',  # ← Change this
    default_args={'owner': 'your_name'},
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['cbs', 'police', 'day_four'],
) as dag:
    # Rest is copy/paste from your examples

    hello_world = BashOperator(
        task_id='hello_world',
        bash_command='echo "The world is my playground! 🌎"'
    )