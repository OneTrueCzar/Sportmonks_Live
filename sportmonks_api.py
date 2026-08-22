import pandas as pd
import requests
from functools import cache
from pathlib import Path
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

#credentials

load_dotenv(Path(__file__).with_name('db_file.env'))
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
api_token = os.getenv('API_TOKEN')

#connect to sql

def get_postgres_engine():
    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(f'Connecting to host: {db_host}, database: {db_name}')
    return create_engine(url)

#sportmonks variables

list_of_calls = ('teams', 'standings', 'stages')

season_ids = {'epl25_26':28083, 'laliga25_26':27965, 'bundesliga25_26':28321, 'serieA25_26': 27895, 'ligueUn25_26':28082}

#sportmonks call

def fetch_call(endpoints=list_of_calls, season_ids=season_ids):
    base_url = "https://api.sportmonks.com/v3/football/"

    def fetch_endpoint(endpoint, season_id):
        response = requests.get(f"{base_url}{endpoint}/seasons/{season_id}?api_token={api_token}", timeout=30)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or "data" not in payload:
            raise KeyError(f"Expected 'data' in response for {endpoint}, got: {payload}")
        return pd.json_normalize(payload["data"])

    return {
        (endpoint, season_name): fetch_endpoint(endpoint, season_id)
        for endpoint in endpoints
        for season_name, season_id in season_ids.items()
    }

#upload to sql

def upload_dataframe(df, engine, table_name):
    df.to_sql(table_name, engine, index=False, if_exists="replace")
    print(f"Uploaded {len(df)} rows and {len(df.columns)} columns to {table_name}")

def process_df(name, df):
    df = df.copy()
    return df

if __name__ == "__main__":
    dfs = fetch_call(list_of_calls, season_ids)
    engine = get_postgres_engine()
    for (name, season_name), df in dfs.items():
        processed_df = process_df(name, df)
        upload_dataframe(processed_df, engine, table_name=f"{name}_{season_name}")
