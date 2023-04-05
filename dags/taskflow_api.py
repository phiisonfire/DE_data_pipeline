from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'Phi_Nguyen',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

@dag(dag_id='dag_with_taskflow_api_v01',
     default_args=default_args,
     start_date=datetime(2023,3,14),
     schedule_interval='@daily')

def hello_world_etl():

    @task()
    def get_name():
        return 'Jerry'
    
    @task()
    def get_age():
        return 19
    
    @task()
    def greet(name, age):
        print(f'Hello this is {name} and i am {age}')
    
    name = get_name()
    age = get_age()
    greet(name=name, age=age)

greet_dag = hello_world_etl()
