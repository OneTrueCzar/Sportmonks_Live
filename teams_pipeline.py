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
        response = requests.get(f'https://api.sportmonks.com/v3/football/teams/seasons/{season_id}?api_token={api_token}&include=statistics.details.type', timeout = 30)
        payload = response.json()
        teams = (
            pd.json_normalize(
                payload['data'])
            .rename(columns={'id':'team_id'})
            .drop(columns='statistics', errors='ignore')
        )
        statistics = (
            pd.json_normalize(
                payload['data'],
                record_path='statistics',
                meta=['id'],
                meta_prefix='parent_',
                errors='ignore')
            .rename(columns={
                'parent_id':'team_statistic_id'
            })
            .drop(columns='details', errors = 'ignore')
        )
        details = (
            pd.json_normalize(
                payload['data'],
                record_path=['statistics', 'details'],
                meta=['team_statistics_id'],
                errors = 'ignore'
            )
            .rename(columns={'type.code': 'type_code'})
        )

        details = details[['team_statistics_id', 'value', 'type_code']]

        details = (
            details.pivot_table(
            index='team_statistics_id',
            columns='type_code',
            values='values',
            aggfunc='first'
            )
        .reset_index()
        )

        stats_merge = statistics.merge(details, on='team_statistics_id', how = 'left')
        stats_merge = stats_merge[['team_id', 'value', 'type_code']]

        stats = (
            stats_merge.pivot_table(
            index='team_id',
            columns='type_code',
            values='values',
            aggfunc='first'
            )
        .reset_index()
        )

        return teams.merge(stats, on = 'team_id', how = 'left')

    return {
        ('teams', season_name): fetch_endpoint(season_id)
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
