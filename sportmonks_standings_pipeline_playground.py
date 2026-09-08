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
    meta_prefix='standing_',
    sep='_'
)

details = details.rename(columns={
    'standing_id': 'standing_id',
    'type_id': 'type_id',
    'type_code': 'stat_column_name'
})

print(details)

"""type_dict = pd.DataFrame(
    [[details['type'][n].get('id'), details['type'][n].get('code')] 
    for n in range(len(details['type']))],
    columns=['type_id', 'stat-column-names']
    )

details_raw = pd.merge(details, type_dict, on = 'type_id')
details_final = details_raw[['standing_id', 'value', 'stat-column-names']]
details_pivot = details_final.pivot(index = 'standing_id', columns = 'stat-column-names', values = 'value')
details_pivot = details_pivot.reset_index()

details_dfs = [pd.DataFrame(rows) for rows in table['details']]
type_dicts = [details_dfs[n]['type'] for n in range(len(details_dfs))]
type_dicts = [
    pd.DataFrame(
        [[detail_type.get('id'), detail_type.get('code')] for detail_type in details_df['type']],
        columns=['type_id', 'stat-column-names']
    )
    for details_df in details_dfs
]"""
