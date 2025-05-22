from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

with DAG(
    dag_id="simple_bash_graph",
    description="Demo DAG showing task dependencies with BashOperator",
    schedule_interval=None,  # Manual trigger only
    start_date=days_ago(1),
    catchup=False,
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["example"],
) as dag:

    bash1 = BashOperator(
        task_id="bash1",
        bash_command='echo "Running bash1 - {{ run_id }}"',
    )

    bash2 = BashOperator(
        task_id="bash2",
        bash_command='echo "Running bash2 - {{ run_id }}"',
    )

    bash3 = BashOperator(
        task_id="bash3",
        bash_command='echo "Running bash3 - {{ run_id }}"',
    )

    bash4 = BashOperator(
        task_id="bash4",
        bash_command='echo "Running bash4 - {{ run_id }}"',
    )

    bash5 = BashOperator(
        task_id="bash5",
        bash_command='echo "Running bash5 - {{ run_id }}"',
    )

    # Set dependencies

    bash1 >> bash2
    bash1 >> bash3
    bash3 >> bash4
    bash2 >> bash5