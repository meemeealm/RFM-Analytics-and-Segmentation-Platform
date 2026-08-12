import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.http.operators.http import HttpOperator

# this script only automates pipeline from MySQL -> BigQuery -> FastAPI Endpoint -> GCS

# Dynamic path setup for local scripts
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PARENT_DIR)

from scripts.load_mysql_to_bq import run_mysql_to_bq

# Default settings applied to ALL tasks
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='customer_segmentation_end_to_end',
    default_args=default_args,
    description='Pipeline: MySQL -> BigQuery -> FastAPI -> GCS',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['segmentation'],
) as dag:

    # ------------------------------------------------------------------
    # TASK 1: EXTRACT & LOAD (Ingestion)
    # ------------------------------------------------------------------
    task_extract_load = PythonOperator(
        task_id='extract_mysql_to_raw_bq',
        python_callable=run_mysql_to_bq,
    )

    # ------------------------------------------------------------------
    # TASK 2: TRANSFORM 
    # ------------------------------------------------------------------
    # SQL query text directly embedded or read from a file
    transformation_sql = """
    CREATE OR REPLACE TABLE `retail.customer_mart.customer_data` AS
    SELECT 
        user_id,
        COALESCE(age, 35) AS age,
        annual_income,
        spending_score
    FROM `customer_mart.customer_data`;
    """

    task_transform_bq = BigQueryInsertJobOperator(
        task_id='transform_raw_to_analytics_bq',
        configuration={
            "query": {
                "query": transformation_sql,
                "useLegacySql": False,
            }
        },
    )

    # ------------------------------------------------------------------
    # TASK 3: INFERENCE (MLOps / FastAPI)
    # ------------------------------------------------------------------

    task_trigger_inference = HttpOperator(
        task_id='trigger_fastapi_segmentation',
        http_conn_id='fastapi_server_default', # Named connection in Airflow UI
        endpoint='run-segmentation',          # Maps to @app.post("/run-segmentation")
        method='POST',
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 200, # Verify API returned 200 OK
    )

    # ------------------------------------------------------------------
    # DECOUPLED PIPELINE DEPENDENCY CHAIN
    # ------------------------------------------------------------------
    task_extract_load >> task_transform_bq >> task_trigger_inference