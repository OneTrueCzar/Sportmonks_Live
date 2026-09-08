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

response = requests.get(f"https://api.sportmonks.com/v3/football/teams/seasons/28083?api_token={api_token}&include=statistics.details.type", timeout=30)
payload = response.json()
details = (
    pd.json_normalize(
        payload['data'],
        record_path=['statistics', 'details'],
        meta=['id'],
        meta_prefix='team_',
        errors='ignore',
        max_level=2
    )
    .rename(columns={'type.code': 'type_code'})
        )

details_values = details.filter(regex='^value.').columns
details_test = details.pivot_table(index = 'team_id', columns = 'type_code', values = details_values)

print(details_values)


