from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id='simple_example_dag',
    start_date=datetime(2023, 1, 1),
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
) as dag:
    start_task = BashOperator(
        task_id='start_task',
        bash_command='echo "Starting the simple example DAG!"',
    )

    sleep_task = BashOperator(
        task_id='sleep_task',
        bash_command='sleep 5',
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "Simple example DAG finished!"',
    )

    start_task >> sleep_task >> end_task
