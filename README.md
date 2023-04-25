# Data Engineering - Create a data pipeline
In this project, I crawled IT jobs information in website itviec.com then used it as the input for my data pipeline. The result is the auto-updated dashboard about IT jobs information from itviec.com
![image](https://user-images.githubusercontent.com/87942974/234226033-0307fa58-a45e-4eac-8bd5-f2eea4f451a3.png)




## 1. Craw web's data using Selenium
- Detail in [craw_itviec.ipynb]
- Result in the csv file contains information of IT jobs
![image](https://user-images.githubusercontent.com/87942974/234229204-38185630-bde6-4b35-9724-80f3f4cd86f7.png)
## 2. ETL Pipeline
In this session I use Docker, Airflow to automate and manage data pipeline. Raw data from Crawl session is stored in Data Lake then Airflow will extract - transform - and load to Data Warehouse for visualization.
![image](https://user-images.githubusercontent.com/87942974/234230387-c3c087c2-c5f5-4c23-ba59-c329c2869ca6.png)
## 3. Visualization
I use Power BI to visualize the insights.
![image](https://user-images.githubusercontent.com/87942974/234230518-d205912b-fc1a-41d4-a978-2e5ca147a81e.png)
![image](https://user-images.githubusercontent.com/87942974/234230632-0c9272ad-2bdd-4697-a03d-073138ee0dea.png)
