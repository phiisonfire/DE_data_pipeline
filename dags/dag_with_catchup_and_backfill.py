from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
# from airflow.hooks.postgres
import sqlalchemy
default_args = {
    'owner': 'Mr.Phi',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def get_pandas():
    print(f'SK learn version: {sqlalchemy.__version__}')

def extract():
    from sqlalchemy import create_engine # , ForeignKey, Column, String, Integer, CHAR
    # from sqlalchemy.orm import sessionmaker, declarative_base
    import pandas as pd

    server = 'PHINGUYEN\SQLEXPRESS'
    database = 'DE_Data_Lake'
    username = 'sa'
    password = 'sapassword'

    # Tạo chuỗi kết nối
    connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

    # Tạo engine kết nối đến máy chủ SQL Server
    engine = create_engine(connection_string, echo=True)

    df = pd.read_sql_table('jobs_v04', engine)
    print(type(df))
    print(len(df))
    # return df

with DAG(
    dag_id='etl_test_connection_v01',
    default_args=default_args,
    description='My first DAG with PythonOperator',
    start_date=datetime(2023, 3, 19),
    schedule_interval='@daily'
) as dag:
    # task1 nhằm truyền các parameter cần thiết vào hàm greet
    task4 = PythonOperator(
        task_id='test_pandas',
        python_callable=get_pandas
    )

    task5 = PythonOperator(
        task_id='extract',
        python_callable=extract
    )

    # khi task được nêu ở đây, các hàm python_callable sẽ được thực thi cùng các parameter được define trong task's definition
    """ 
    task2 thực thi function get_name, push return value 'Jerry' vào XCOMS
    task1 pull return value của hàm get_name, gán vào biến name thông qua line name = ti.xcoms_pull(task_id='get_name')
    sau đó task 1 thực thi python_callable function greet
    """
    """
    Ta có thể truyền parameter vào function (của task) thông qua Xcoms hoặc op_kwargs
    """
    task4 >> task5