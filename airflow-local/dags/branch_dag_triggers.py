from airflow import DAG
from airflow.decorators import task, dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

with DAG(
    dag_id="false_dag",
    description="Showing triggering other dags",
) as false_dag:
    @task
    def first_task():
        print("I am the first false task")

    @task
    def second_task():
        print("I am the second false task")

    first_task() >> second_task()

with DAG(
    dag_id="true_dag",
    description="Showing triggering other dags",
) as true_dag:
    @task
    def first_task():
        print("I am the first true task")

    @task
    def second_task():
        print("I am the second true task")

    first_task() >> second_task()

with DAG(
    dag_id="decision_dag",
    description="Using a branch operator to decide on the branch we take"
) as dag: 
    @task
    def preparation():
        print("I lied I prepare nothing")

        minutes = datetime.now().minute
        return minutes

    @task.branch
    def choose_branch(xcom_minutes):
        print("I shall now choose your future")


        if xcom_minutes % 2 == 1:
            print("I have decided on truth!") 
            return "true_trigger"

        return "false_trigger"

    true_trigger = TriggerDagRunOperator(
        task_id="true_trigger",
        trigger_dag_id="true_dag",  # Ensure this equals the dag_id of the DAG to trigger
        conf={"message": "I am the Truth"},
    )
    false_trigger = TriggerDagRunOperator(
        task_id="false_trigger",
        trigger_dag_id="false_dag",  # Ensure this equals the dag_id of the DAG to trigger
        conf={"message": "The other one lies"},
    )

    prepare_task = preparation()


    prepare_task >> choose_branch(prepare_task) >> [true_trigger, false_trigger]