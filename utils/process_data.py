"""
utils/process_data.py

This module provides functions for computing statistical summaries (team and league averages)
and merging them with raw dataframes, commonly used for fantasy baseball analysis.
"""

import pandas as pd
# No longer importing STAT_CATEGORIES here, it should be in config.py if needed elsewhere.

def compute_stat_summary(df: pd.DataFrame, stat_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes average statistics per team and the overall league average for a given stat.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing 'team', 'week', and the 'stat_col' data.
                       Expected columns: 'team', 'week', and the column specified by `stat_col`.
    stat_col (str): The name of the column containing the statistical data
                    for which to compute averages (e.g., 'HR', 'R', 'K').

    Returns:
    tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames:
        - team_avg_df (pd.DataFrame): Contains the average of `stat_col` for each team
                                      across all weeks, with columns 'team' and `stat_col`.
        - league_avg_df (pd.DataFrame): Contains the overall league average of `stat_col`
                                        for each week, with columns 'week' and `stat_col`
                                        and an added 'team' column set to "League Average".
    """
    # Create a copy to avoid modifying the original DataFrame passed as argument
    df_copy = df.copy()

    # Convert the stat column to numeric, coercing invalid entries to NaN
    # This is crucial for numerical operations and robustness.
    df_copy[stat_col] = pd.to_numeric(df_copy[stat_col], errors='coerce')

    # Drop rows where the stat column has NaN values after conversion
    df_copy = df_copy.dropna(subset=[stat_col])

    # Calculate team averages across all weeks
    team_avg_df = df_copy.groupby("team")[stat_col].mean().reset_index()
    # Rename the stat_col in team_avg_df to avoid conflicts if merging multiple stats later
    team_avg_df.rename(columns={stat_col: f"{stat_col}_team_avg"}, inplace=True)


    # Calculate league average per week
    league_avg_df = df_copy.groupby("week")[stat_col].mean().reset_index()
    league_avg_df["team"] = "League Average" # Add a placeholder team name for merging purposes
    # Rename the stat_col in league_avg_df
    league_avg_df.rename(columns={stat_col: f"{stat_col}_league_avg"}, inplace=True)

    return team_avg_df, league_avg_df


def merge_all_stats(df: pd.DataFrame, stat_col: str) -> pd.DataFrame:
    """
    Merges raw statistical data with team-level and league-level weekly averages
    for a specified stat column.

    This function first computes the average statistics using `compute_stat_summary`
    and then merges these averages back into the original DataFrame.

    Parameters:
    df (pd.DataFrame): The raw DataFrame containing per-team, per-week statistical data.
                       Expected to have 'team' and 'week' columns.
    stat_col (str): The name of the statistical column (e.g., 'HR', 'R', 'K')
                    for which to perform the merge.

    Returns:
    pd.DataFrame: The DataFrame with the original data augmented with
                  new columns for the team average (`<stat_col>_team_avg`)
                  and league average (`<stat_col>_league_avg`) for the specified stat.
    """
    team_avg_df, league_avg_df = compute_stat_summary(df, stat_col)

    # Merge team-level averages: merge team_avg_df into df on the 'team' column.
    # The suffix ensures that the original 'stat_col' in df is preserved
    # and the new average column is clearly named (e.g., 'HR_team_avg').
    merged = df.merge(team_avg_df, on="team", how="left")

    # Merge league-level averages: merge league_avg_df into the partially merged DataFrame
    # on the 'week' and 'team' columns.
    merged = merged.merge(league_avg_df, on=["week", "team"], how="left")

    # Removed the line `merged = merged.rename(columns={"team": "team"})`
    # as it was redundant and likely a leftover from previous iterations.

    return merged
