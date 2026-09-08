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

response = requests.get(f"https://api.sportmonks.com/v3/football/standings/seasons/28083?api_token={api_token}&include=participant;details.type", timeout=30)
payload = response.json()
table = pd.json_normalize(payload['data'], max_level=2)
details = pd.json_normalize(
    payload['data'],
    record_path='details',
    meta=['id'],
    meta_prefix='parent_',
    sep='_'
)

#print(details)

expanded = table.explode('details', ignore_index=True)

detail_columns = pd.json_normalize(expanded.pop('details'))

details_long = pd.concat(
    [
        expanded[['id']].rename(columns={'id': 'standing_id'}),
        detail_columns
    ],
    axis=1
)

details_wide = (
    details_long
    .pivot_table(
        index='standing_id',
        columns='type_code',
        values='value',
        aggfunc='first'
    )
    .reset_index()
)

details_wide.columns.name = None

parent_table = (
    table
    .drop(columns='details')
    .rename(columns={'id': 'standing_id'})
)

table_with_details = parent_table.merge(
    details_wide,
    on='standing_id',
    how='left'
)

print(table_with_details)
