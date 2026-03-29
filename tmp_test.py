import sys
sys.path.append(r'c:\Users\frogg\Documents\python_scripts\fanatsy_sports\espn_fantasy\espn_flb_inseason\mlb_fantasy_dashboard_V2')
import pandas as pd
from utils.rankings_utilities import get_tables

url = 'https://pitcherlist.com/fantasy-reliever-rankings-closers-holds-solds-3-26/'
dfs = get_tables(url)
valid_dfs = []
for k, df in dfs.items():
    cols = list(df.columns)
    if 'Rank' in cols and any(c in cols for c in ['Pitcher', 'Hitter', 'Player', 'Name']):
        valid_dfs.append((k, df))

for i, (k, df) in enumerate(valid_dfs):
    print(f'Index {i}: {k} with {len(df)} rows. Title/1st row Rank: {df.iloc[0]["Rank"]}')
