import pandas as pd
import requests
from functools import cache
from pathlib import Path
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('db_file.env'))
db_user = os.getenv('DB_USER')
db_pw = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
api_token = os.getenv('API_TOKEN')
api_token = os.getenv('API_TOKEN')

endpoint = "https://api.sportmonks.com/v3/football/rounds/seasons/"
season_ids = {'epl25_26':28083, 'laliga25_26':27965, 'bundesliga25_26':28321, 'serieA25_26': 27895, 'ligueUn25_26':28082}

def postgresql_engine():
    url = f"postgresql+psycopg2://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)

def api_call(endpoint = endpoint, season_ids = season_ids):

    def fetch_endpoint(endpoint, season_id):
        response = requests.get(f"{endpoint}{season_id}?api_token={api_token}", timeout=30)
        payload = response.json()
        return pd.json_normalize(payload["data"])

    return{
        (endpoint, season_name): fetch_endpoint(endpoint, season_id)
        for season_name, season_id in season_ids.items()
    }

def upload_df(df, engine, table_name):
    df.to_sql(table_name, engine, index = False, if_exists = 'replace')
    print(f"Uploaded {len(df)} rows and {len(df.columns)} columns to {table_name}")

def process_df(name, df):
    df = df.copy()
    return df

if __name__ == '__main__':
    dfs = api_call(endpoint, season_ids)
    engine = postgresql_engine()
    for (name, season_name), df in dfs.items():
        processed_df = process_df(name, df)
        upload_df(processed_df, engine, table_name = f"{name}_{season_name}")