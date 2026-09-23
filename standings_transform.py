import pandas as pd
from standings_extract import extract_step

transform_step = pd.json_normalize(extract_step)

print(transform_step)