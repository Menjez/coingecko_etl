#!/usr/bin/env python3
import requests
import psycopg2 as pg
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time

DB_NAME = "database_name"
DB_USER = "username"
DB_PASSWORD = "password"
DB_HOST = "wsl host on windows"
DB_PORT = "5432"

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 28),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --- DAG Definition ---
dag = DAG(
    'coin_gecko_dag',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
    tags=['coin', 'postgres', 'etl']
)


def extract():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    coin_ids = [
        "bitcoin", "binancecoin", "cardano", "dogecoin", "ethereum",
        "litecoin", "monero", "polkadot", "ripple", "shiba-inu",
        "solana", "stellar", "tether", "tron", "the-open-network", "usd-coin"
    ]
    params = {
        "ids": ",".join(coin_ids),
        "vs_currency": "USD" 
    }
    max_retries = 5
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"Rate limited by API. Retry {attempt + 1} of {max_retries} after delay.")
            time.sleep(60)  # wait 60 seconds before retrying
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    return None

def transform(**context):

    raw_data = context['task_instance'].xcom_pull(task_ids='extract_coin_data')
    if not raw_data:
        raise ValueError("No data pulled from extract task.")

    cleaned_data = []
    for coin in raw_data:
        cleaned_data.append({
            'Name':coin['name'], 
            'Symbol':coin['symbol'].upper(),
            'Current Price':coin['current_price'], 
            'Market Cap':coin['market_cap'],
            'Total Volume':coin['total_volume']
        })   
    return cleaned_data


def load(**context):

    clean_data = context['task_instance'].xcom_pull(task_ids='transform_data')
    if not clean_data:
        raise ValueError("No cleaned data received from transform task.")
    
    try:
        conn = pg.connect(
            dbname=DB_NAME, 
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cursor = conn.cursor()

        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS coin_gecko;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_gecko.coin_data (
                coin text,
                symbol text,       
                current_price numeric,
                market_cap bigint,
                total_volume bigint,
                timestamp timestamp
            );
        """)

        insert_query = """
            INSERT INTO coin_gecko.coin_data 
            (coin, symbol, current_price, market_cap, total_volume, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        now = datetime.now()

        rows_to_insert = []
        for coin in clean_data:
            rows_to_insert.append((
                coin['Name'],
                coin['Symbol'],
                coin['Current Price'],
                coin['Market Cap'],
                coin['Total Volume'],
                now
            ))
        
        cursor.executemany(insert_query, rows_to_insert)
        conn.commit()
    except Exception as e:
        print(f"Database Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()   

extract_task = PythonOperator(
    task_id='extract_coin_data',
    python_callable=extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data_to_postgres',
    python_callable=load,
    dag=dag
)

# --- Task Dependencies ---
extract_task >> transform_task >> load_task
