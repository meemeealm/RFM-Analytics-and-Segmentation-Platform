import os
import pandas as pd
from sqlalchemy import create_engine
from google.cloud import bigquery
from dotenv import load_dotenv

# Load database credentials from .env file
load_dotenv()

def run_mysql_to_bq():
    # 1. Build Connection Engine to your local MySQL
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    # Connection string format for SQLAlchemy + PyMySQL 
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(connection_string)
    
    # 2. Extract data using Pandas
    query = "SELECT customer_id, invoicedate, quantity, unitprice FROM users;"
    print("Connecting to MySQL Workbench and extracting data...")
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        print("No new data found in MySQL. Skipping upload.")
        return

    # 3. Stream data straight to BigQuery
    bq_client = bigquery.Client()
    table_id = "customer_mart.customer_data"
    
    # WRITE_TRUNCATE overwrites the BQ table daily with the fresh snapshot from MySQL
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    print(f"Syncing {len(df)} records into BigQuery...")
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for confirmation
    
    print("Database synchronization successful!")

if __name__ == "__main__":
    run_mysql_to_bq()