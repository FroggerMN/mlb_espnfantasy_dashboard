import logging
import os
from typing import Dict, List

import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_object_dtype,
)

from utils.rankings_utilities import clean_players_names

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
PAGE_TITLE = "Athletic Rankings"
DATA_DIR = "data/googlesheets/"
SESSION_STATE_ROSTER_KEY = "ROSTERS_DF"


@st.cache_data
def load_csv_files(data_dir: str) -> List[str]:
    """Retrieves a list of CSV files from the specified directory."""
    try:
        return [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    except FileNotFoundError:
        logger.error(f"Directory not found: {data_dir}")
        return []


def load_and_process_rankings(file_list: List[str], roster_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Loads and processes ranking data from CSV files."""
    rankings_dict = {}
    for file in file_list:
        file_path = os.path.join(DATA_DIR, file)
        try:
            df = pd.read_csv(file_path)

            if len(df.columns) > 1:
                df.columns = [df.columns[0]] + ["Player Names"] + df.columns[2:].tolist()

            df_clean = clean_players_names(df, "Player Names")

            merged_df = pd.merge(
                df_clean,
                roster_df[["Player Names", "Team Names"]],
                on="Player Names",
                how="left",
            )

            merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
            
            if "Team Names" in merged_df.columns:
                cols = ["Team Names"] + [col for col in merged_df.columns if col != "Team Names"]
                merged_df = merged_df[cols]
            
            rankings_dict[file] = merged_df
            logger.info(f"Successfully loaded and processed {file}")

        except Exception as e:
            logger.error(f"Error loading {file}: {e}")
            st.error(f"Error loading {file}: {e}")
    
    return rankings_dict


def filter_dataframe(df: pd.DataFrame, key_prefix: str) -> pd.DataFrame:
    """Adds UI for filtering the dataframe based on columns."""
    modify = st.checkbox("Add filters", value=True, key=f"{key_prefix}_filter_toggle")
    if not modify:
        return df

    df_filtered = df.copy()

    for col in df_filtered.columns:
        if is_object_dtype(df_filtered[col]):
            try:
                df_filtered[col] = pd.to_datetime(df_filtered[col], format="%m/%d/%Y")
            except Exception:
                pass
        elif is_datetime64_any_dtype(df_filtered[col]):
            if df_filtered[col].dt.tz is not None:
                df_filtered[col] = df_filtered[col].dt.tz_localize(None)

    to_filter_columns = st.multiselect(
        "Filter dataframe on",
        df_filtered.columns,
        default=["Team Names"] if "Team Names" in df_filtered.columns else None,
        key=f"{key_prefix}_filter_columns",
    )

    for column in to_filter_columns:
        if df_filtered[column].nunique() < 15:
            default_vals = (
                ["RP's, We Have Da Heat", "Available"]
                if column == "Team Names"
                else list(df_filtered[column].unique())
            )
            # Filter default vals to only those present in df
            valid_defaults = [val for val in default_vals if val in df_filtered[column].unique()]

            user_vals = st.multiselect(
                f"Values for {column}",
                list(df_filtered[column].unique()),
                default=valid_defaults,
                key=f"{key_prefix}_{column}_select",
            )
            df_filtered = df_filtered[df_filtered[column].isin(user_vals)]

    return df_filtered


def main():
    """Main Streamlit page logic."""
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    st.title(PAGE_TITLE)

    if SESSION_STATE_ROSTER_KEY not in st.session_state or st.session_state[SESSION_STATE_ROSTER_KEY].empty:
        st.error("🚨 No roster data available in session state.")
        return

    roster_df = st.session_state[SESSION_STATE_ROSTER_KEY]
    
    csv_files = load_csv_files(DATA_DIR)
    if not csv_files:
        st.warning("No CSV files found for rankings.")
        return

    rankings_dict = load_and_process_rankings(csv_files, roster_df)

    if not rankings_dict:
        st.warning("No ranking data could be processed.")
        return

    tabs = st.tabs(list(rankings_dict.keys()))

    for i, (key, df) in enumerate(rankings_dict.items()):
        with tabs[i]:
            st.subheader(key)
            filtered_df = filter_dataframe(df, key)
            st.dataframe(filtered_df, width='stretch')


if __name__ == "__main__":
    main()
