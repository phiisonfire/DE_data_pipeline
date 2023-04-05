import time
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from airflow.hooks.base import BaseHook
import pandas as pd
from sqlalchemy import create_engine
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'Mr.Phi',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

#extract tasks
def get_src_tables():
    hook = MsSqlHook(mssql_conn_id="ssms")
    sql = """ select  t.name as table_name  
     from sys.tables t where t.name in ('jobs','jobs_v02') """
    df = hook.get_pandas_df(sql)
    print(df)
    tbl_dict = df.to_dict('dict')
    return tbl_dict

with DAG(
    dag_id='etl_test_v03',
    default_args=default_args,
    description='My first DAG with PythonOperator',
    start_date=datetime(2023, 3, 19),
    schedule_interval='@daily'
) as dag:
    # task1 nhằm truyền các parameter cần thiết vào hàm greet
    task4 = PythonOperator(
        task_id='test_pandas',
        python_callable=get_src_tables
    )

    task4
