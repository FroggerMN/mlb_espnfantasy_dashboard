import streamlit as st
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import os
from utils.rankings_utilities import clean_players_names

# --- League Info from Session ---
#YEAR = st.session_state.YEAR
#LEAGUE_ID = st.session_state.LEAGUE_ID
#SCORING_PERIOD_ID = st.session_state.SCORING_PERIOD_ID
#ESPN_S2 = st.session_state.ESPN_S2
#SWID = st.session_state.SWID
ROSTER_DF = st.session_state.ROSTERS_DF

# Set up the page
st.set_page_config(page_title="Athletic Rankings", layout="wide")
st.title("Athletic Rankings")

# Get the list of CSV files
csv_files = [f for f in os.listdir('data/googlesheets/') if f.endswith('.csv')]

# Create a dictionary to store the rankings data
rankings_dict = {}

# Loop through the CSV files
for file in csv_files:
    try:
        # Read the CSV file
        df = pd.read_csv(f'data/googlesheets/{file}')

        # Select the first two columns
        #df = df.iloc[:, :2]

        # Rename the second column to "Player Names"
        if len(df.columns) > 1:  # Ensure there's at least two columns
            df.columns = [df.columns[0]] + ['Player Names'] + df.columns[2:].tolist()


        # Clean the player names
        df_clean = clean_players_names(df, 'Player Names')

        # Merge the dataframe with the ROSTER_DF
        merged_df = pd.merge(
            df_clean,
            ROSTER_DF[["Player Names", "Team Names"]],
            on="Player Names",
            how="left",
        )

        # Fill NaN values in "Team Names" with "Available"
        merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
        if "Team Names" in merged_df.columns:
            cols = ["Team Names"] + [col for col in merged_df.columns if col != "Team Names"]
            merged_df = merged_df[cols]  # Reorder DataFrame columns
        # Add the merged dataframe to the rankings_dict
        rankings_dict[file] = merged_df
    except Exception as e:
        st.error(f"Error loading {file}: {e}")

# Create tabs for each rankings data
tabs = st.tabs([file for file in csv_files])

# --- Filterable Table Function ---
def filter_dataframe(df: pd.DataFrame, key_prefix: str) -> pd.DataFrame:
    modify = st.checkbox("Add filters", value=True, key=f"{key_prefix}_filter_toggle")
    if not modify:
        return df

    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format="%m/%d/%Y")
            except Exception:
                pass
        elif is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    to_filter_columns = st.multiselect(
        "Filter dataframe on",
        df.columns,
        default=["Team Names"],
        key=f"{key_prefix}_filter_columns",
    )

    for column in to_filter_columns:
        if df[column].nunique() < 15:
            default_vals = (
                [ "RP's, We Have Da Heat", "Available"]
                if column == "Team Names"
                else list(df[column].unique())
            )
            user_vals = st.multiselect(
                f"Values for {column}",
                df[column].unique(),
                default=default_vals,
                key=f"{key_prefix}_{column}_select",
            )
            df = df[df[column].isin(user_vals)]

    return df

# --- Display Ranking Tabs ---
for i, key in enumerate(csv_files):
    with tabs[i]:
        st.subheader(i)
        df = rankings_dict[key]
        filtered_df = filter_dataframe(df, key)

        st.dataframe(filtered_df, use_container_width=True)


