import logging
import pandas as pd
import requests
from io import StringIO

logger = logging.getLogger(__name__)

def fetch_sit_start_data(url: str) -> pd.DataFrame:
    """
    Fetches the Pitcher List Sit/Start article and parses all the daily tables.
    Returns a normalized DataFrame of all starting pitchers for the week.
    """
    try:
        logger.info(f"Fetching Sit/Start data from {url}")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        tables = pd.read_html(StringIO(response.text))
        logger.info(f"Found {len(tables)} tables in Sit/Start article.")
        
        all_pitchers = []
        
        for table in tables:
            header_idx = None
            for i, row in table.iterrows():
                row_str = str(row.values)
                if "Game" in row_str and "Away Pitcher" in row_str:
                    header_idx = i
                    break
                    
            if header_idx is not None:
                df = table.iloc[header_idx + 1:].copy()
                # Use the header row for column names, but ensure no duplicate names crash dictionary accesses
                col_names = table.iloc[header_idx].values
                # We know the columns should roughly be:
                # [Date, Game, Away Pitcher, Sit / Start (Away), Home Pitcher, Sit / Start (Home)]
                
                # We'll just use positional indices for safety since 'Sit / Start' is repeated.
                # Col 0: Date
                # Col 1: Game
                # Col 2: Away Pitcher
                # Col 3: Away Sit/Start
                # Col 4: Home Pitcher
                # Col 5: Home Sit/Start
                
                if len(col_names) >= 6:
                    for _, row in df.iterrows():
                        game_str = str(row.iloc[1]).strip()
                        if pd.isna(row.iloc[1]) or game_str == "" or game_str == "nan":
                            continue
                            
                        away_team, home_team = "", ""
                        if " at " in game_str:
                            parts = game_str.split(" at ")
                            if len(parts) == 2:
                                away_team = parts[0].strip()
                                home_team = parts[1].strip()
                        
                        date_str = str(row.iloc[0]).strip()
                        
                        away_pitcher = row.iloc[2]
                        away_sit_start = row.iloc[3]
                        
                        home_pitcher = row.iloc[4]
                        home_sit_start = row.iloc[5]
                        
                        if pd.notna(away_pitcher) and str(away_pitcher).strip() != "" and str(away_pitcher).strip() != "nan":
                            all_pitchers.append({
                                'Player Names': str(away_pitcher).strip(),
                                'MLB Team': away_team,
                                'Opponent': f"@{home_team}",
                                'Sit/Start Rating': str(away_sit_start).strip(),
                                'Date': date_str
                            })
                            
                        if pd.notna(home_pitcher) and str(home_pitcher).strip() != "" and str(home_pitcher).strip() != "nan":
                            all_pitchers.append({
                                'Player Names': str(home_pitcher).strip(),
                                'MLB Team': home_team,
                                'Opponent': f"vs {away_team}",
                                'Sit/Start Rating': str(home_sit_start).strip(),
                                'Date': date_str
                            })
                            
        result_df = pd.DataFrame(all_pitchers)
        logger.info(f"Successfully extracted {len(result_df)} pitcher matchups.")
        return result_df
    except Exception as e:
        logger.error(f"Error fetching sit/start data from {url}: {e}")
        return pd.DataFrame()
