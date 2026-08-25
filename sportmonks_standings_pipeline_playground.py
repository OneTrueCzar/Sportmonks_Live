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
table = pd.json_normalize(payload['data'])
table = table.rename(columns = {'id': 'standing_id'})
details = pd.DataFrame(table['details'][0])

type_dict = pd.DataFrame(
    [[details['type'][n].get('id'), details['type'][n].get('code')] 
    for n in range(len(details['type']))],
    columns=['type_id', 'stat-column-names']
    )

details_raw = pd.merge(details, type_dict, on = 'type_id')
details_final = details_raw[['standing_id', 'value', 'stat-column-names']]

#print(details_final)

#Have to get rid of the multi-index next where first column is the 'standing_id' and the rest are the stat values

details_pivot = details_final.pivot(index = 'standing_id', columns = 'stat-column-names', values = 'value')
print(details_pivot.index)