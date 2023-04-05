from airflow import DAG # import class DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Dictionary
default_args = {
    'owner':'Mr.Phi',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

# Create dag instance
with DAG(
    dag_id='phi_first_dag_v3',
    default_args=default_args,
    description='This is Phis first dag',
    start_date=datetime(2023,3,14,15),
    schedule_interval='@daily'
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command='echo hello world, this is the first task!'
    )

    task2 = BashOperator(
        task_id='second_task',
        bash_command='echo this is task 2'
    )

    task3 = BashOperator(
        task_id='third_task',
        bash_command='echo this is task 3'
    )

    task1.set_downstream(task2)
    task1.set_downstream(task3)