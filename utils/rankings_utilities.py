"""
utils/rankings_utilities.py

This module provides utility functions for processing and cleaning player ranking data,
including fetching HTML tables from URLs and standardizing player names.
"""

import pandas as pd
import requests
from io import StringIO
from typing import Dict, List, Union

def get_tables(web_path: str) -> Dict[str, pd.DataFrame]:
    """
    Fetches HTML tables from a given web path and returns them as a dictionary of DataFrames.

    Parameters:
    web_path (str): The URL of the webpage containing the tables.

    Returns:
    Dict[str, pd.DataFrame]: A dictionary where keys are formatted as 'df_N' (e.g., 'df_1', 'df_2')
                             and values are the corresponding pandas DataFrames parsed from the HTML tables.

    Raises:
    requests.exceptions.RequestException: If there's an issue fetching the URL (e.g., network error, bad status code).
    ValueError: If no tables are found on the webpage or if the HTML content cannot be parsed.
    """
    response = requests.get(web_path, verify=True)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

    df_dict = {}
    try:
        # Read the HTML content into a list of DataFrames
        df_list = pd.read_html(StringIO(response.text))

        if not df_list:
            raise ValueError(f"No HTML tables found on the page: {web_path}")

        for i, table in enumerate(df_list):
            df_dict[f'df_{i+1}'] = table
    except ValueError as e:
        # Catch errors from pd.read_html if no tables are found or parsing fails
        raise ValueError(f"Failed to parse tables from {web_path}: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors during table processing
        raise Exception(f"An unexpected error occurred processing tables from {web_path}: {e}") from e

    return df_dict

def clean_players_names(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Cleans player names in the specified DataFrame column by converting to lowercase
    and applying a series of string replacements using regular expressions.

    Args:
        df (pd.DataFrame): The input DataFrame containing player names.
        column_name (str): The name of the column in `df` containing the player names
                           to be cleaned.

    Returns:
        pd.DataFrame: A new DataFrame with the specified column containing cleaned player names.
                      Returns a copy to avoid modifying the original DataFrame in place.
    """
    # Create a copy to ensure the original DataFrame is not modified in place.
    df_cleaned = df.copy()

    # Ensure the column exists and contains string-like data
    if column_name not in df_cleaned.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    # Convert the column to string type, handling potential NaN values
    df_cleaned[column_name] = df_cleaned[column_name].astype(str)

    # Convert to lowercase first
    df_cleaned[column_name] = df_cleaned[column_name].str.lower()

    # Define replacements using regex patterns
    replacements = {
        'é': 'e', ' jr.': '', 'ó': 'o', 'á': 'a', 'ñ': 'n', 'ú': 'u', 'í': 'i', "'": '', # Remove apostrophes
        # Regex to handle initials like "F.M." -> "FM"
        r'\b(\w)\.(\w)\.': r'\1\2',
        # Remove common fantasy data artifacts or special characters:
        # (dh) -> (DH designation), brackets, plus, asterisk, caret, 't' followed by digit (team ID perhaps)
        r'[\(\)\[\]\+\*\^]|t\d+': '', # Changed from [()+^*] for clarity
        r'\d+$': '' # Remove trailing digits
    }

    # Apply replacements iteratively
    for pattern, replacement in replacements.items():
        # Ensure pattern is treated as regex if it contains special characters
        df_cleaned[column_name] = df_cleaned[column_name].str.replace(pattern, replacement, regex=True)

    return df_cleaned

def full_name_2_initial_last(full_name: str) -> str:
    """
    Converts a full player name to a "first initial. last name" format.

    Args:
        full_name (str): The full name of the player (e.g., "Ronald Acuña Jr.").

    Returns:
        str: The name in "first initial. last name" format (e.g., "R. Acuña Jr.").
             Returns an empty string if the input `full_name` is empty or cannot be processed.
    """
    if not isinstance(full_name, str) or not full_name.strip():
        return "" # Handle non-string or empty inputs

    parts = full_name.strip().split()

    if not parts:
        return "" # Handle cases where split results in an empty list

    last_name = parts[-1]
    first_initial = parts[0][0] # Get the first character of the first part

    # Handle cases where first_initial might be empty if parts[0] was empty string
    if not first_initial:
        return ""

    initial_last = f"{first_initial}. {last_name}"
    return initial_last
