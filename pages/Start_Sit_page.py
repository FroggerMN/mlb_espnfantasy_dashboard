# pages/Start_Sit_page.py

import logging
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
from pandas.api.types import is_datetime64_any_dtype, is_object_dtype

# Potentially uncomment if constants from config are truly used here
# from utils.config import LEAGUE_ID, YEAR, SCORING_PERIOD_ID

# Initialize logger for this module
logger = logging.getLogger(__name__)

# --- Constants ---
PAGE_TITLE = 'Start Sit Analysis'
SESSION_STATE_ROSTER_KEY = 'ROSTERS_DF' # Consistent key for session state

# --- Utility Functions ---

def _convert_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts object columns to datetime if possible, handling potential errors.
    Ensures datetime columns are timezone-naive.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with converted columns.
    """
    df_processed = df.copy()
    for col in df_processed.columns:
        if is_object_dtype(df_processed[col]):
            try:
                # Use raw string for format to avoid SyntaxWarning
                # Use errors='coerce' to turn unparseable dates into NaT
                df_processed[col] = pd.to_datetime(df_processed[col], format=r'%m/%d/%Y', errors='coerce')
                logger.debug(f"Column '{col}' successfully converted to datetime.")
            except Exception as e:
                # Log a warning but allow processing to continue
                logger.warning(f"Could not convert object column '{col}' to datetime: {e}")
        elif is_datetime64_any_dtype(df_processed[col]):
            # Ensure datetime columns are timezone-naive for consistency
            if df_processed[col].dt.tz is not None:
                df_processed[col] = df_processed[col].dt.tz_localize(None)
                logger.debug(f"Timezone removed from datetime column '{col}'.")
    return df_processed

def filter_dataframe(df: pd.DataFrame, team_names: List[str]) -> pd.DataFrame:
    """
    Filters the input DataFrame based on user-selected team names and converts data types.

    Args:
        df (pd.DataFrame): The input DataFrame, expected to contain "start/sit" data.
        team_names (List[str]): A list of team names to include in the filtered DataFrame.

    Returns:
        pd.DataFrame: The filtered and type-converted DataFrame.
    """
    if df.empty:
        logger.info("Empty DataFrame passed to filter_dataframe. Returning empty DataFrame.")
        return pd.DataFrame()

    # Step 1: Data Type Conversion
    df_filtered = _convert_dataframe_columns(df)

    # Step 2: Filter by team names
    if team_names and 'team' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['team'].isin(team_names)]
        logger.info(f"Filtered DataFrame by selected teams: {team_names}")
    elif team_names: # team_names provided but 'team' column is missing
        logger.warning("Team names provided for filtering, but 'team' column not found in DataFrame.")

    return df_filtered

def _display_data_section(df: pd.DataFrame) -> None:
    """
    Displays the filtered DataFrame and provides options for further analysis.
    """
    st.subheader("Filtered Start/Sit Data")

    # Add interactive filtering/search if desired
    # For instance, a search box for player names
    search_query = st.text_input("Search Player Name", "")
    if search_query:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    if df.empty:
        st.info("No data matches the current selections or filters. Please adjust your selections.")
        return

    st.dataframe(df, use_container_width=True)

    # Example: Highlight duplicate player names (if a 'Player Name' column exists)
    if 'Player Name' in df.columns:
        duplicate_players = df[df.duplicated(subset=['Player Name'], keep=False)]
        if not duplicate_players.empty:
            st.warning("Potential duplicate player names found in filtered data:")
            st.dataframe(duplicate_players[['Player Name']].drop_duplicates())

    # Example: Calculate and display basic team totals (requires specific columns like 'points')
    # This section would need more context on your 'start/sit' data structure
    # if 'Team Name' in df.columns and 'Points' in df.columns:
    #     st.subheader("Team Totals (Example)")
    #     team_totals = df.groupby('Team Name')['Points'].sum().reset_index()
    #     st.dataframe(team_totals)


# --- Streamlit Page Layout ---
def main_page_logic():
    """
    Main function to define the Streamlit page layout and logic.
    """
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    st.title(PAGE_TITLE)
    st.markdown("""
    Welcome to the **Start/Sit Analysis** page.
    This module helps you review and filter player data to make informed
    start/sit decisions for your fantasy baseball team.
    """)

    st.write("---") # Separator for visual clarity

    # Check if ROSTERS_DF is available in session state
    if SESSION_STATE_ROSTER_KEY not in st.session_state or st.session_state[SESSION_STATE_ROSTER_KEY].empty:
        st.error("🚨 No start/sit data available in session state.")
        st.info(f"""
            Please ensure that the main dashboard page (`app.py`)
            or a dedicated data loading utility successfully fetches and
            populates `st.session_state['{SESSION_STATE_ROSTER_KEY}']`
            before navigating to this page.
            Data is typically loaded from the ESPN API or other sources.
        """)
        logger.error(f"'{SESSION_STATE_ROSTER_KEY}' not found or empty in session state.")
        return # Stop execution if no data is available

    raw_data_df = st.session_state[SESSION_STATE_ROSTER_KEY]
    logger.info(f"Loaded {len(raw_data_df)} rows from '{SESSION_STATE_ROSTER_KEY}'.")

    st.subheader("Data Overview")
    st.info("This is a preview of the raw data loaded. Use the sidebar to filter.")
    st.dataframe(raw_data_df.head(), use_container_width=True)

    # --- Sidebar for Filtering Options ---
    st.sidebar.header("Filter Options")

    # Dynamic Team Name filter (assuming 'team' or 'Team Name' column exists in ROSTERS_DF)
    team_column_name = None
    if 'team' in raw_data_df.columns:
        team_column_name = 'team'
    elif 'Team Name' in raw_data_df.columns:
        team_column_name = 'Team Name'

    selected_teams = []
    if team_column_name:
        all_teams = sorted(raw_data_df[team_column_name].dropna().unique().tolist())
        selected_teams = st.sidebar.multiselect(
            "Select Team(s) to Display",
            options=all_teams,
            default=all_teams # Default to showing all teams
        )
        logger.info(f"Sidebar team selection: {selected_teams}")
    else:
        st.sidebar.info("No 'team' or 'Team Name' column found for filtering by team.")

    # Apply filtering
    filtered_df = filter_dataframe(raw_data_df, selected_teams)

    # Display filtered data section
    _display_data_section(filtered_df)

# Entry point for the Streamlit application
if __name__ == "__main__":
    main_page_logic()
