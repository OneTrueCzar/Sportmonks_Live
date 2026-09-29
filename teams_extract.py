import polars as pl
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('db_file.env'))
api_token = os.getenv('API_TOKEN')

season_ids = {'epl26_27':28083, 'laliga26_27':27965, 'bundesliga26_27':28321, 'serieA26_27': 27895, 'ligueUn26_27':28082}

def api_call(season_ids):

    def fetch_endpoint(season_id):
        response = requests.get(f'https://api.sportmonks.com/v3/football/teams/seasons/{season_id}?api_token={api_token}&include=statistics.details.type', timeout=30)
        payload = response.json()
        return pl.json_normalize(payload['data'])

    return {
        (f'standings_{season_name}'): fetch_endpoint(season_id)
        for season_name, season_id in season_ids.items()
    }

teams_extract_step = api_call(season_ids)