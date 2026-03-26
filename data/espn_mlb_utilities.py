"""
data/espn_mlb_utilities.py

This module provides utility functions for extracting, transforming, and calculating
fantasy baseball statistics from ESPN MLB data. It includes functions for retrieving
league information, roster details, and weekly statistical results.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Union
from data.fetch_espn_data import fetch_espn_data  # Import if fetch_espn_data is needed
from utils.rankings_utilities import clean_players_names
from utils.id_maps import STATS_MAP
from utils.config import TARGET_STATS, STAT_COMPONENTS  # Import from config.py
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create reverse STATS_MAP
REVERSE_STATS_MAP: Dict[str, int] = {v: k for k, v in STATS_MAP.items()}

# Generate ALL_STATS and related constants dynamically
ALL_STATS: set = set(TARGET_STATS) 
for stat in TARGET_STATS:
    ALL_STATS.update(STAT_COMPONENTS.get(stat, []))

STAT_IDS: List[int] = [REVERSE_STATS_MAP[s] for s in ALL_STATS]
STAT_DICT: Dict[int, str] = {REVERSE_STATS_MAP[s]: s for s in ALL_STATS}


import os
import json
import streamlit as st

@st.cache_data
def load_view_json(view: str, league_id: int, year: int, scoring_period_id: int, data_dir: str = 'data') -> Dict:
    """
    Loads ESPN view data from a JSON file, using Streamlit's caching mechanism.

    Args:
        view (str): The name of the ESPN view (e.g., 'mTeam', 'mRoster', 'mBoxscore').
        league_id (int): The ID of the ESPN fantasy league.
        year (int): The year of the fantasy baseball season.
        scoring_period_id (int): The scoring period ID (typically the week number).
        data_dir (str): The base directory where the JSON files are stored.

    Returns:
        Dict: A dictionary containing the parsed JSON data from the file.

    Raises:
        FileNotFoundError: If the specified JSON file does not exist.
        json.JSONDecodeError: If the file exists but contains invalid JSON.
    """
    filename = f"espn_json/{view}_{league_id}_{year}_{scoring_period_id}.json"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found. Please refresh data first.")

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
        raise  # Re-raise the exception to be handled upstream


def get_league_info(mTeam: Dict) -> pd.DataFrame:
    """
    Extracts league information (Team Number, Team Names) from ESPN API data.

    Args:
        mTeam (Dict): A dictionary containing team data from the ESPN API,
                      typically obtained from the 'mTeam' view.  Expected to have
                      a 'teams' key whose value is a list of team dictionaries. Each
                      team dictionary is expected to have a 'name'.

    Returns:
        pd.DataFrame: A DataFrame containing the league information,
                      with columns 'Team Number' and 'Team Names'.
                      Returns an empty DataFrame if the input data is invalid or empty.
    """
    teams = mTeam.get('teams', [])
    if not isinstance(teams, list):
        logger.warning("Unexpected structure for mTeam['teams'], returning empty DataFrame")
        return pd.DataFrame()
    try:
        data = [{'Team Number': i + 1, 'Team Names': team['name']} for i, team in enumerate(teams)]
        df = pd.DataFrame(data)
        return df
    except KeyError as e:
        logger.error(f"KeyError extracting league info: {e}")
        return pd.DataFrame()


def get_roster_info(mRoster: Dict, mTeams: Dict) -> pd.DataFrame:
    """
    Extracts roster information (Team Number, Player Names, Team Names) from ESPN API data.

    Args:
        mRoster (Dict): A dictionary containing roster data from the ESPN API,
                        typically obtained from the 'mRoster' view.  Expected to have
                        a 'teams' key whose value is a list of team dictionaries.  Each
                        team dictionary is expected to have 'roster' (a dictionary)
                        and 'entries' (a list of player entries). Each entry should have
                        'playerPoolEntry' and 'player' and 'fullName'.        mTeams (Dict): A dictionary containing team information from the ESPN API,
                       typically obtained from the 'mTeam' view. Expected to have a
                       'teams' key whose value is a list of team dictionaries. Each
                       team dictionary is expected to have an 'id' and a 'name'.

    Returns:
        pd.DataFrame: A DataFrame containing the cleaned roster information,
                      with columns 'Team Number', 'Player Names', and 'Team Names'.
                      Returns an empty DataFrame if the input data is invalid or empty.
    """
    records: List[Dict[str, Union[int, str]]] = []

    if not isinstance(mRoster, dict) or not isinstance(mTeams, dict):
        logger.error("Invalid mRoster or mTeams input")
        return pd.DataFrame()

    teams_data = mRoster.get('teams')    
    
    if not isinstance(teams_data, list):
        logger.error("Invalid mRoster['teams'] structure")
        return pd.DataFrame()

    for i, team in enumerate(teams_data, start=1):
        if not isinstance(team, dict):
            logger.warning(f"Invalid team structure in mRoster['teams'] at index {i-1}")
            continue  # Skip to the next team

        roster_data = team.get('roster')
        if not isinstance(roster_data, dict):
            logger.warning(f"Invalid roster structure for team {i}")
            continue

        entries = roster_data.get('entries')
        if not isinstance(entries, list):
            logger.warning(f"Invalid entries structure for team {i}")
            continue

        for entry in entries:
            try:
                full_name = entry['playerPoolEntry']['player']['fullName']
                records.append({'Team Number': i, 'Player Names': full_name})
            except (KeyError, TypeError) as e:
                logger.error(f"Missing key or invalid data structure for player in team {i}: {e}")
                continue

    teamIds_player_df = pd.DataFrame(records)

    teamNames_df = get_league_info(mTeams)
    if teamNames_df.empty:
        logger.warning("Could not retrieve league info")
        return pd.DataFrame()

    rosters_df = pd.merge(teamIds_player_df, teamNames_df, on='Team Number', how='left')

    rosters_df = rosters_df.rename(columns={'Pitcher': 'Player Names', 'Hitter': 'Player Names', 'Player': 'Player Names'})
    rosters_df_clean = clean_players_names(rosters_df, 'Player Names')

    return rosters_df_clean


def stat_melt_and_rename(df: pd.DataFrame, id_vars: List[str], value_vars: List[str], var_name: str, value_name: str, team_col: str) -> pd.DataFrame:
    """
    Melts a DataFrame from wide to long format and renames columns for consistency.

    Args:
        df (pd.DataFrame): The input DataFrame.
        id_vars (List[str]): Columns to keep as identifier variables.
        value_vars (List[str]): Columns to melt into the 'value' column.
        var_name (str): The name to use for the new column containing the original column names.        value_name (str): The name to use for the new column containing the values.
        team_col (str): The original column name containing the team ID.

    Returns:
        pd.DataFrame: The melted and renamed DataFrame.
    """
    try:
        melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name)
        melted.rename(columns={team_col: 'teamId'}, inplace=True)
        melted['StatId'] = melted['StatId'].str.extract(r'(\d+)', expand=False).astype(int) # Explicitly convert to int
        return melted
    except Exception as e:
        logger.exception("Error in stat_melt_and_rename")
        return pd.DataFrame() # Return empty DataFrame on error


def get_weekresults(df_schedule: pd.DataFrame, df_teams: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts week-by-week stat results for all teams, handling home/away symmetry.

    Args:
        df_schedule (pd.DataFrame): DataFrame containing the schedule data.
        df_teams (pd.DataFrame): DataFrame containing the team data.

    Returns:
        pd.DataFrame: DataFrame containing the processed weekly results.
    """
    try:
        home_keys = [f'home.cumulativeScore.scoreByStat.{stat_id}' for stat_id in STAT_IDS]
        away_keys = [f'away.cumulativeScore.scoreByStat.{stat_id}' for stat_id in STAT_IDS]

        home_results = stat_melt_and_rename(
            df_schedule, ['home.teamId', 'matchupPeriodId'],
            [f'{key}.result' for key in home_keys], 'StatId', 'Win/Loss', 'home.teamId'
        )
        away_results = stat_melt_and_rename(
            df_schedule, ['away.teamId', 'matchupPeriodId'],
            [f'{key}.result' for key in away_keys], 'StatId', 'Win/Loss', 'away.teamId'
        )

        home_scores = stat_melt_and_rename(            df_schedule, ['home.teamId', 'matchupPeriodId'],
            [f'{key}.score' for key in home_keys], 'StatId', 'Score', 'home.teamId'
        )
        away_scores = stat_melt_and_rename(            df_schedule, ['away.teamId', 'matchupPeriodId'],
            [f'{key}.score' for key in away_keys], 'StatId', 'Score', 'away.teamId'
        )

        winloss = pd.concat([home_results, away_results])
        scores = pd.concat([home_scores, away_scores])

        df = pd.merge(scores, winloss, on=['teamId', 'matchupPeriodId', 'StatId'], how='outer')

        team_map = pd.Series(df_teams['name'].values, index=df_teams['id']).to_dict()
        df['Team Names'] = df['teamId'].map(team_map)

        df['Stat Name'] = df['StatId'].astype(int).map(STAT_DICT)

        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0)

        return df
    except Exception as e:
        logger.exception("Error in get_weekresults")
        return pd.DataFrame()


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates additional metrics (win_loss, Stat Ave, Matchup Stat Ave, Stat Win Ave) for a DataFrame
    containing weekly fantasy baseball statistics.

    Args:
        df (pd.DataFrame): The input DataFrame with weekly stat data.
                           Expected columns: 'Win/Loss', 'Stat Name', 'Score', 'matchupPeriodId'.

    Returns:
        pd.DataFrame: The DataFrame with added metrics.
    """
    try:
        df['win_loss'] = df['Win/Loss'].apply(lambda x: 'W' if x == 'WIN' else 'L')
        df['Stat Ave'] = df.groupby('Stat Name')['Score'].transform('mean')
        df['Matchup Stat Ave'] = df.groupby(['Stat Name', 'matchupPeriodId'])['Score'].transform('mean')

        win_means = df[df['Win/Loss'] == 'WIN'].groupby('Stat Name')['Score'].mean().rename('Stat Win Ave')
        df = df.merge(win_means, on='Stat Name', how='left')

        return df
    except Exception as e:
        logger.exception("Error in calculate_metrics")
        return pd.DataFrame()


def recalculate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Correct AVG, ERA, WHIP using summed components per team/week.

    Args:
        df (pd.DataFrame): The input DataFrame with weekly stat data and components.
                           Expected columns: "Team Names", "matchupPeriodId", "Stat Name", "Score".

    Returns:
        pd.DataFrame: The DataFrame with corrected AVG, ERA, and WHIP values.
    """
    try:
        df = df.copy()

        # H / AB -> AVG
        hits = df[df["Stat Name"] == "H"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        at_bats = df[df["Stat Name"] == "AB"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        avg = (hits / at_bats).replace([np.inf, -np.inf], np.nan).fillna(0)
        avg = avg.reset_index().assign(**{"Stat Name": "AVG"})

        # (ER / (OUTS / 3))*9 -> ERA
        er = df[df["Stat Name"] == "ER"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        outs = df[df["Stat Name"] == "OUTS"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        era = ((er / (outs / 3)) * 9).replace([np.inf, -np.inf], np.nan).fillna(0)
        era = era.reset_index().assign(**{"Stat Name": "ERA"})

        # (P_BB + P_H) / (OUTS / 3) -> WHIP
        p_bb = df[df["Stat Name"] == "P_BB"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        p_h = df[df["Stat Name"] == "P_H"].groupby(["Team Names", "matchupPeriodId"])["Score"].sum()
        whip = ((p_bb + p_h) / (outs / 3)).replace([np.inf, -np.inf], np.nan).fillna(0)
        whip = whip.reset_index().assign(**{"Stat Name": "WHIP"})

        # Combine all corrected ratio stats
        fixed_ratios = pd.concat([avg, era, whip], ignore_index=True)
        fixed_ratios.rename(columns={0: "Score"}, inplace=True)

        # Remove old rows for these stat names
        df = df[~df["Stat Name"].isin(["AVG", "ERA", "WHIP"])]

        return pd.concat([df, fixed_ratios], ignore_index=True)
    except Exception as e:
        logger.exception("Error in recalculate_ratios")
        return pd.DataFrame()


@st.cache_data
def get_category_stats(league_id: int, year: int, scoring_period_id: int) -> pd.DataFrame:
    """
    Compute cleaned and corrected stat metrics for fantasy scoring.

    Args:
        league_id (int): The ID of the ESPN fantasy league.
        year (int): The year of the fantasy baseball season.
        scoring_period_id (int): The scoring period ID (typically the week number).

    Returns:
        pd.DataFrame: A DataFrame containing the processed category statistics.
    """
    try:
        data = load_view_json("mBoxscore", league_id, year, scoring_period_id)

        if 'schedule' not in data or 'teams' not in data:
            raise ValueError("mBoxscore JSON is missing required keys: 'schedule' or 'teams'.")

        schedule = pd.json_normalize(data['schedule'])[:-6]  # Drop playoff matchups
        teams = pd.json_normalize(data['teams'])

        # Extract and compute
        results = get_weekresults(schedule, teams)
        results = recalculate_ratios(results)
        results = calculate_metrics(results)

        return results    
    
    except Exception as e:
        logger.exception(f"Error in get_category_stats for league_id={league_id}, year={year}, scoring_period_id={scoring_period_id}")
        return pd.DataFrame()  # Return an empty DataFrame on error
