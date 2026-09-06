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

season_ids = {'epl25_26':28083, 'laliga25_26':27965, 'bundesliga25_26':28321, 'serieA25_26': 27895, 'ligueUn25_26':28082}

def postgresql_engine():
    url = f"postgresql+psycopg2://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}"
    print(f'Connecting to host: {db_host}, database: {db_name}')
    return create_engine(url)

def api_call(season_ids):

    def fetch_endpoint(season_id):
        response = requests.get(f"https://api.sportmonks.com/v3/football/standings/seasons/{season_id}?api_token={api_token}&include=participant;details.type", timeout=30)
        payload = response.json()
        standings = (
            pd.json_normalize(payload["data"])
            .rename(columns={"id": "standings_id"})
            .drop(columns="details", errors="ignore")
        )
        detail_rows = []
        for standing in payload["data"]:
            standings_id = standing.get("id", standing.get("standing_id"))
            for detail in standing.get("details") or []:
                detail_row = detail.copy()
                detail_type = detail_row.pop("type", {}) or {}
                if isinstance(detail_type, dict):
                    detail_row["type_id"] = detail_type.get("id", detail_row.get("type_id"))
                    detail_row["type_code"] = detail_type.get("code", detail_row.get("type_code"))
                detail_row["standings_id"] = standings_id
                detail_rows.append(detail_row)

        details = pd.json_normalize(detail_rows)[
            ["standings_id", "value", "type_code"]
        ]

        if not details.empty:
            details = (
                details.pivot_table(
                    index="standings_id",
                    columns="type_code",
                    values="value",
                    aggfunc="first",
                )
                .reset_index()
            )
            details.columns.name = None

        return standings.merge(details, on="standings_id", how="left")

    return{
        ('standings', season_name): fetch_endpoint(season_id) 
        for season_name, season_id in season_ids.items()
    }

def upload_df(df, engine, table_name):
    df.to_sql(table_name, engine, index = False, if_exists = 'replace')
    print(f"Uploaded {len(df)} rows and {len(df.columns)} columns to {table_name}")

def process_df(name, df):
    df = df.copy()
    return df

if __name__ == '__main__':
    dfs = api_call(season_ids)
    engine = postgresql_engine()
    for (name, season_name), df in dfs.items():
        processed_df = process_df(name, df)
        upload_df(processed_df, engine, table_name = f"{name}_{season_name}")