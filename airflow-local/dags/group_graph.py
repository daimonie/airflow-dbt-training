from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.decorators import task_group, task, dag
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import timedelta

with DAG(
    dag_id="remote_graph",
    description="Showing triggering other dags",
) as dag:
    trigger = TriggerDagRunOperator(
        task_id="test_trigger_dagrun",
        trigger_dag_id="group_graph",  # Ensure this equals the dag_id of the DAG to trigger
        conf={"message": "Hello World"},
    )
    bash1 = BashOperator(
        task_id="bash1",
        bash_command='echo "Running bash1 - {{ run_id }}"',
    )
    trigger >> bash1

with DAG(
    dag_id="group_graph",
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

    with TaskGroup(group_id="stealth") as group:
        bash2 = BashOperator(
            task_id="bash2",
            bash_command='echo "Running bash2 - {{ run_id }}"',
        )

        bash3 = BashOperator(
            task_id="bash3",
            bash_command='echo "Running bash3 - {{ run_id }}"',
        )
        with TaskGroup(group_id="substealth") as subgroup:

            bash4 = BashOperator(
                task_id="bash4",
                bash_command='echo "Running bash4 - {{ run_id }}"',
            )   
            bash6 = BashOperator(
                task_id="bash6",
                bash_command='echo "Running bash6 - {{ run_id }}"',
            )
            bash4 >> bash6

        bash2 >> bash3, subgroup
    bash5 = BashOperator(
        task_id="bash5",
        bash_command='echo "Running bash5 - {{ run_id }}"',
    )


    # Set dependencies
    bash1 >> group
    group >> bash5

