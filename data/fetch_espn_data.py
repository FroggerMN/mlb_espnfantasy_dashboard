"""
data/fetch_espn_data.py

This module provides functions for fetching data from the ESPN Fantasy Baseball API,
saving the data to JSON files, and retrieving player maps. It uses the `requests`
library for making HTTP requests and the `espn_api.baseball` library for
interacting with the ESPN API.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import requests
import streamlit as st
from espn_api.baseball import League
from espn_api.baseball.box_score import BoxScore

# Initialize logger (assuming it's configured elsewhere)
logger = logging.getLogger(__name__)

def save_dict_to_json_file(data_dict: Dict[str, Any], file_path: str) -> None:
    """
    Saves a dictionary to a JSON file.

    Args:
        data_dict (Dict[str, Any]): The dictionary to save.
        file_path (str): The full path (including .json extension) to the output file.
    """
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, indent=4, sort_keys=True)
        logger.info(f"Saved data to {file_path}")
    except Exception as e:
        logger.exception(f"Error saving data to {file_path}")

def fetch_espn_data(
    year: int,
    league_id: int,
    view: str,
    scoring_period_id: int,
    espn_s2_cookie: Optional[str] = None,
    swid_cookie: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches raw data from the ESPN Fantasy Baseball API.

    Args:
        year (int): The season year.
        league_id (int): The ESPN league ID.
        view (str): The data view to request (e.g., 'mTeam', 'mRoster', 'mBoxscore').
        scoring_period_id (int): The scoring week ID.
        espn_s2_cookie (Optional[str], optional): The ESPN S2 cookie. Defaults to None.
        swid_cookie (Optional[str], optional): The SWID cookie. Defaults to None.

    Returns:
        Dict[str, Any]: The parsed JSON response from the API.
    """
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/FLB/seasons/{year}/segments/0/leagues/{league_id}"
    logger.debug(f"Fetching ESPN data from URL: {url} with view={view}, period={scoring_period_id}")

    cookies = {}
    if swid_cookie:
        cookies['SWID'] = swid_cookie
    if espn_s2_cookie:
        cookies['espn_s2'] = espn_s2_cookie

    params = {'view': view, 'scoringPeriodId': scoring_period_id}

    try:
        response = requests.get(url, params=params, cookies=cookies or None, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error fetching ESPN data from {url}: {e}")
        return {}  # Return an empty dict on error


def fetch_and_save_view( # Renamed from mView_dict
    year: int,
    league_id: int,
    scoring_period_id: int,
    view: str,
    espn_s2_cookie: Optional[str] = None,
    swid_cookie: Optional[str] = None
) -> Dict[str, Any]:
    """    Fetches ESPN data for a specific view and saves it to a JSON file.

    Args:
        year (int): The season year.
        league_id (int): The ESPN league ID.
        scoring_period_id (int): The scoring week ID.
        view (str): The data view to request (e.g., 'mTeam', 'mRoster', 'mBoxscore').
        espn_s2_cookie (Optional[str], optional): The ESPN S2 cookie. Defaults to None.
        swid_cookie (Optional[str], optional): The SWID cookie. Defaults to None.

    Returns:
        Dict[str, Any]: The data fetched from the ESPN API.
    """
    try:
        data = fetch_espn_data(
            year=year,
            league_id=league_id,
            view=view,
            scoring_period_id=scoring_period_id,
            espn_s2_cookie=espn_s2_cookie,
            swid_cookie=swid_cookie,
        )
        file_path = f"data/espn_json/{view}_{league_id}_{year}_{scoring_period_id}.json"
        save_dict_to_json_file(data, file_path)
        return data
    except Exception as e:
        logger.exception(f"Error fetching and saving view {view} for league {league_id}, year {year}, period {scoring_period_id}")
        return {} # Return empty dict on error

def get_league(
    league_id: int,
    season_year: int,
    espn_s2_cookie: str,
    swid_cookie: str
) -> League:
    """
    Instantiates and returns a League object using the `espn_api.baseball` library.

    Args:
        league_id (int): The ESPN league ID.
        season_year (int): The season year.
        espn_s2_cookie (str): The ESPN S2 cookie.
        swid_cookie (str): The SWID cookie.

    Returns:
        League: An instance of the ESPN League class.
    """
    try:
        return League(
            league_id=league_id,
            year=season_year,
            espn_s2=espn_s2_cookie,
            swid=swid_cookie
        )
    except Exception as e:
        logger.exception(f"Error instantiating League object for league {league_id}, year {season_year}")
        raise # Re-raise the exception.  This is likely a fatal error.

def get_espn_player_map(
    league_id: int,
    season_year: int,
    espn_s2_cookie: str,
    swid_cookie: str,
    cache_file: str = 'player_map.json'
) -> pd.DataFrame:
    """
    Retrieves the ESPN player map, using a cached file if available.

    Args:
        league_id (int): The ESPN league ID.
        season_year (int): The season year.
        espn_s2_cookie (str): The ESPN S2 cookie.
        swid_cookie (str): The SWID cookie.
        cache_file (str, optional): The name of the cache file. Defaults to 'player_map.json'.

    Returns:
        pd.DataFrame: A DataFrame containing the player data.
    """
    try:
        if os.path.exists(cache_file):
            logger.info("Using cached player map.")
            return pd.read_json(cache_file)

        league = get_league(league_id, season_year, espn_s2_cookie, swid_cookie)
        player_data_df = pd.DataFrame.from_dict(league.player_map, orient='index')
        player_data_df.to_json(cache_file)
        return player_data_df
    except Exception as e:
        logger.exception(f"Error retrieving ESPN player map for league {league_id}, year {season_year}")
        return pd.DataFrame() # Return empty DataFrame on error