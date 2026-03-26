"""
data/fetch_pitcherlist_ranking.py

This module provides functions for fetching and processing player rankings and
"start/sit" data from the PitcherList website. It relies on web scraping and
Pandas for data manipulation.
"""

import pandas as pd
from data.espn_mlb_utilities import get_league_info, get_roster_info  # Import if needed
from utils.rankings_utilities import get_tables, clean_players_names, full_name_2_initial_last
from typing import List, Tuple, Dict
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Consider moving this to a config file or database for easier updates
# Or make it user-configurable via the Streamlit UI
PITCHERLIST_RANKINGS_LIST: List[Tuple[str, str, str]] = [
    ('https://pitcherlist.com/top-100-starting-pitchers-for-2025-fantasy-baseball-week-8-5-19/', '4', 'sp_100_df'),
    ('https://pitcherlist.com/rp-ranks-5-23-the-top-100-relievers-for-savehold-leagues//', '3', 'sh_100_df'),
    ('https://pitcherlist.com/top-150-hitters-for-fantasy-baseball-2025-week-8-5-22/', '1', 'hitters_150_df')
]

def get_pitcherlist_tables(url: str, table_number: str) -> pd.DataFrame:
    """
    Fetches and processes table data from the specified URL.

    Args:
        url (str): The URL of the webpage containing the table.
        table_number (str): The identifier of the table on the webpage (e.g., '1', '2').

    Returns:
        pd.DataFrame: Processed DataFrame with pitcher list data.
                      Returns an empty DataFrame if an error occurs.
    """
    try:
        dfs = get_tables(url)
        df = dfs[f'df_{table_number}'].copy()
        df.rename(columns={'Pitcher': 'Player Names', 'Hitter': 'Player Names', 'Player': 'Player Names'}, inplace=True)
        return df
    except KeyError:
        logger.error(f"Table 'df_{table_number}' not found in {url}")
        return pd.DataFrame()
    except Exception as e:
        logger.exception(f"Error fetching or processing table from {url}")
        return pd.DataFrame()

def get_pitcherlist_rankings(pitchersList_rankings_list: List[Tuple[str, str, str]]) -> Dict[str, pd.DataFrame]:
    """
    Fetches and processes player rankings from a list of PitcherList URLs.

    Args:
        pitchersList_rankings_list (List[Tuple[str, str, str]]): A list of tuples, where each tuple
            contains the URL, table number, and a unique identifier for the ranking (e.g., 'sp_100_df').

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are the unique identifiers for the rankings
            and values are the corresponding processed DataFrames.
    """
    pitcherList_dfs: Dict[str, pd.DataFrame] = {}
    for url, table_number, ranking_id in pitchersList_rankings_list:
        try:
            df = get_pitcherlist_tables(url, table_number)
            df = clean_players_names(df, 'Player Names')
            pitcherList_dfs[ranking_id] = df
        except Exception as e:
            logger.exception(f"Error processing ranking from {url}")
            pitcherList_dfs[ranking_id] = pd.DataFrame() # Store an empty DataFrame to avoid issues later

    return pitcherList_dfs

def pitcherlist_start_sit(url: str, roster_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetches and processes "start/sit" data from the specified PitcherList URL.

    Args:
        url (str): The URL of the webpage containing the "start/sit" data.
        roster_df (pd.DataFrame): DataFrame containing roster information.

    Returns:
        pd.DataFrame: Processed DataFrame with "start/sit" data.
                       Returns an empty DataFrame if an error occurs.
    """
    try:
        dfs = get_tables(url)
        all_dfs = []

        for key, df in dfs.items():
            all_dfs.append(df)

        if not all_dfs:
            logger.warning(f"No tables found on {url}")
            return pd.DataFrame()

        df_append = pd.concat(all_dfs, ignore_index=True)

        # This regex is VERY specific to the PitcherList website structure.
        # Consider making it more robust or configurable.
        df_append = df_append[~df_append[0].str.contains(r'(?:\.children\.\[\d+\]){4}', na=False)]

        # Extract data
        if len(df_append.columns) >= 6: # Check if enough columns exist
            df1 = df_append.iloc[:, [0, 1, 2, 3]].copy()
            df1.columns = ["Date", "Game", "Player Names", "Action"]
            df2 = df_append.iloc[:, [0, 1, 4, 5]].copy()
            df2.columns = ["Date", "Game", "Player Names", "Action"]
            result_df = pd.concat([df1, df2], ignore_index=True)
        else:
            logger.warning(f"Unexpected number of columns on {url}")
            return pd.DataFrame()


        result_df = clean_players_names(result_df, 'Player Names')
        result_df['Players Names'] = result_df['Player Names'].apply(full_name_2_initial_last)

        result_df[['Action', 'Value']] = result_df['Action'].str.split('-', expand=True)

        rosterinitial_df = roster_df.copy()  # avoid modifying original
        rosterinitial_df['Player Names'] = rosterinitial_df['Player Names'].apply(full_name_2_initial_last)

        result_df = pd.merge(result_df, rosterinitial_df[['Player Names', 'Team Names']], on='Player Names', how='left')
        result_df['Team Names'] = result_df['Team Names'].fillna('Available')

        result_df.sort_values(by='Value', ascending=False, inplace=True)
        return result_df

    except Exception as e:
        logger.exception(f"Error processing start/sit data from {url}")
        return pd.DataFrame()