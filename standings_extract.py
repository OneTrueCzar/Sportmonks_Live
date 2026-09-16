import pandas as pd
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('db_file.env'))
api_token = os.getenv('API_TOKEN')

season_ids = {'epl25_26':28083, 'laliga25_26':27965, 'bundesliga25_26':28321, 'serieA25_26': 27895, 'ligueUn25_26':28082}

def api_call(season_ids):

    def fetch_endpoint(season_id):
        response = requests.get(f"https://api.sportmonks.com/v3/football/standings/seasons/{season_id}?api_token={api_token}&include=participant;details.type", timeout=30)
        payload = response.json()
        return pd.json_normalize(payload['data'])

    return {
        (f'standings_{season_name}'): fetch_endpoint(season_id)
        for season_name, season_id in season_ids.items()
    }

extract_step = api_call(season_ids)