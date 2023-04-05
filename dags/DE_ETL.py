from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'Mr.Phi',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def etl():
    # Extract data from Data Lake
    from sqlalchemy import create_engine # , ForeignKey, Column, String, Integer, CHAR
    # from sqlalchemy.orm import sessionmaker, declarative_base
    import pandas as pd
    import numpy as np

    server = 'host.docker.internal:1433'
    datalake = 'DE_Data_Lake'
    username = 'sa'
    password = 'sapassword'

    # Tạo chuỗi kết nối
    connection_string_to_DL = f'mssql+pyodbc://{username}:{password}@{server}/{datalake}?driver=ODBC+Driver+17+for+SQL+Server'

    # Tạo engine kết nối đến máy chủ SQL Server
    engine_to_DL = create_engine(connection_string_to_DL, echo=True)

    # Query table jobs_v03 từ Data Lake
    df_to_load = pd.read_sql_table('jobs_v03', engine_to_DL)

    # Transform table jobs_v03 into 2 table job_df and company_df

    # Drop duplicate
    # len(df_to_load)
    df_to_load_dropped_duplicated = df_to_load.drop_duplicates(subset=['job_url'],keep='first')
    # len(df_to_load_dropped_duplicated)
    # df_to_load_dropped_duplicated = df_to_load_dropped_duplicated.reset_index()

    # Load tables into Data Warehouse
    from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
    from sqlalchemy.orm import sessionmaker, declarative_base
    import pandas as pd

    # server = 'host.docker.internal:1433'
    datawarehouse = 'DE_Data_Warehouse'
    # username = 'sa'
    # password = 'sapassword'

    # Tạo chuỗi kết nối
    connection_string_to_DW = f'mssql+pyodbc://{username}:{password}@{server}/{datawarehouse}?driver=ODBC+Driver+17+for+SQL+Server'

    # Tạo engine kết nối đến máy chủ SQL Server
    engine_to_DW = create_engine(connection_string_to_DW, echo=True)

    Base = declarative_base()

    class Job(Base):
        __tablename__ = 'job_df'

        id = Column(Integer, primary_key=True)
        query = Column(String)
        job_url = Column(String)
        title = Column(String)
        tags = Column(String)
        skill = Column(String)
        # salary = Column(String)
        company_name = Column(String)
        below_salary = Column(Integer)
        upper_salary = Column(Integer)
        avg_salary = Column(Integer)
        salary_info = Column(String)
        
        def __init__(self, row):
            self.id = row.id
            self.query = row.query
            self.job_url = row.job_url
            self.title = row.title
            self.tags = row.tags
            self.skill = row.skill
            self.company_name = row.company_name
            self.below_salary = row.below_salary
            self.upper_salary = row.upper_salary
            self.avg_salary = row.avg_salary
            self.salary_info = row.salary_info


    class Company(Base):
        __tablename__ = 'company_df'

        company_id = Column(Integer, primary_key=True)
        company_name = Column(String)
        company_type = Column(String)
        company_people = Column(String)
        company_working_day = Column(String)
        company_ot = Column(String)
        company_nation = Column(String)
        
        def __init__(self, row):
            self.company_id = row.company_id
            self.company_name = row.company_name
            self.company_type = row.company_type
            self.company_people = row.company_people
            self.company_working_day = row.company_working_day
            self.company_ot = row.company_ot
            self.company_nation = row.company_nation

    # create databases defined in Base if these databases do not exist in the sql server
    Base.metadata.create_all(engine_to_DW)

    # Retrie current information in DW

    # This query fetch the column [job_url] in table job_df
    job_url_list_in_DW_query = 'SELECT job_url FROM job_df'

    job_url_in_DW = pd.read_sql_query(job_url_list_in_DW_query, engine_to_DW)
    job_url_in_DW['is_job_in_DW'] = 1

    # This query fetch the column [company_name] in table company_df
    company_name_in_DW_query = 'SELECT company_name FROM company_df'

    company_name_in_DW = pd.read_sql_query(company_name_in_DW_query, engine_to_DW)
    company_name_in_DW['is_company_in_DW'] = 1

    # Fetch id of the last record in table job_df
    id_of_last_job_record_query = 'SELECT TOP 1 id FROM job_df ORDER BY id DESC'
    id_of_last_job_record = pd.read_sql_query(id_of_last_job_record_query, engine_to_DW)

    # Fetch company id of the last record in table company_df
    id_of_last_company_record_query = 'SELECT TOP 1 company_id FROM company_df ORDER BY company_id DESC'
    id_of_last_company_record = pd.read_sql_query(id_of_last_company_record_query, engine_to_DW)

    
    merge_with_job = df_to_load_dropped_duplicated.merge(job_url_in_DW, on='job_url', how='left')
    new_job_records = merge_with_job[merge_with_job['is_job_in_DW'].isna()]
    new_job_records.drop(['id'],axis=1,inplace=True)
    new_job_records['id'] = 0
    new_job_records[['below_salary','upper_salary','avg_salary','salary_info']] = 0
    new_job_records = new_job_records[['id','query','job_url','title','tags','skill','company_name','below_salary','upper_salary','avg_salary','salary_info', 'salary']]

    if id_of_last_job_record.empty:
        job_id = 1
    else:
        job_id = id_of_last_job_record
    job_id

    for _,row in new_job_records.iterrows():
        new_job_records.loc[_,'id'] = job_id
        job_id += 1

    # Process table job_df
    # job_df = df_dropped[['query','job_url', 'title', 'tags', 'skill', 'salary', 'company_name']]
    # import numpy as np
    # job_df[['below_salary','upper_salary','avg_salary','salary_info']] = 0
    for _, row in new_job_records.iterrows():
        if 'USD' in row.salary:
            salary_str = row.salary.replace(',' , '')
            # print(_)
            # print('True')
            p_dash = salary_str.index('-')
            p_U = salary_str.index('U')
            new_job_records.loc[_,'below_salary'] = int(salary_str[ : p_dash-1])
            new_job_records.loc[_,'upper_salary'] = int(salary_str[p_dash+1 : p_U-1])
            new_job_records.loc[_,'avg_salary']   = (new_job_records.loc[_,'below_salary'] + new_job_records.loc[_,'upper_salary'])/2
            new_job_records.loc[_,'salary_info']   = 'full'
        
        elif any(substring in row.salary for substring in ['You', 'nego', 'attra', 'compe', 'Nego', 'Compe', 'Attra']):
            new_job_records.loc[_,'salary'] = 'Negotiation'
            new_job_records.loc[_,'salary_info']   = 'nego'
        
        elif 'Up to $' in row.salary:
            salary_str = row.salary.replace(',' , '')
            p_dollar_sign = salary_str.index('$')
            new_job_records.loc[_,'upper_salary'] = int(salary_str[p_dollar_sign+1 : p_dollar_sign+5])
            new_job_records.loc[_,'salary_info']   = 'semi'

        else:
            new_job_records.loc[_,'salary'] = 'Negotiation'
            new_job_records.loc[_,'salary_info']   = 'nego'
    
    df_to_load_dropped_duplicated_company = df_to_load.drop_duplicates(subset=['company_name'],keep='first')
    merge_with_company = df_to_load_dropped_duplicated_company.merge(company_name_in_DW, on='company_name', how='left')
    new_company_records = merge_with_company[merge_with_company['is_company_in_DW'].isna()]
    new_company_records.drop(['id'],axis=1,inplace=True)

    new_company_records['company_id'] = 0

    if id_of_last_job_record.empty:
        company_id = 1
    else:
        company_id = id_of_last_job_record

    for _,row in new_company_records.iterrows():
        new_company_records.loc[_,'company_id'] = company_id
        company_id += 1

    # Process table company_df
    new_company_records = new_company_records[['company_id','company_url', 'company_name', 'company_type', 'company_people',
        'company_working_day', 'company_ot', 'company_nation']].drop_duplicates(subset=['company_name'], keep='first')
    for _, row in new_company_records.iterrows():
        if row.company_ot == 'nan':
            row.company_ot = 'No information'
    
    # Create a session
    Session = sessionmaker(bind=engine_to_DW)
    session = Session()

    # row_loaded = 0
    for _, row in new_job_records.iterrows():
        job = Job(row)
        session.add(job)
        # row_loaded += 1
        # print(f'Row loaded = {row_loaded}')

    for _, row in new_company_records.iterrows():
        company = Company(row)
        session.add(company)

    session.commit()
    print('Load done...')

with DAG(
    dag_id='ETL_final_v02',
    default_args=default_args,
    description='Extract raw data from Data Lake, Transform with Pandas then Load it to Data Warehouse',
    start_date=datetime(2023, 3, 22),
    schedule_interval='@daily'
) as dag:
 
    task1 = PythonOperator(
        task_id='ETL',
        python_callable=etl,
    )

    task1