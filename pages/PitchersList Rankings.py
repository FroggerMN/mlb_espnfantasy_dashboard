import streamlit as st
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from data.fetch_pitcherlist_ranking import get_pitcherlist_tables
from utils.rankings_utilities import clean_players_names

import json
import os

URLS_FILE = "data/pitcherslist_urls.json"

# Load URLs from file if available, otherwise use defaults
def load_urls():
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "sp_100_df": "https://pitcherlist.com/top-100-starting-pitchers-for-2025-fantasy-baseball-week-8-5-19/",
            "sh_100_df": "https://pitcherlist.com/rp-ranks-5-23-the-top-100-relievers-for-savehold-leagues//",
            "hitters_150_df": "https://pitcherlist.com/top-150-hitters-for-fantasy-baseball-2025-week-8-5-22/",
        }

pitcherslist_urls = load_urls()
st.session_state.rankings_urls = pitcherslist_urls  # Ensure they persist in session


# --- Page Setup ---
st.set_page_config("PitchersList SP100", layout="wide")
st.title("🎯 PitchersList Rankings Dashboard")

# --- League Info from Session ---
YEAR = st.session_state.YEAR
LEAGUE_ID = st.session_state.LEAGUE_ID
SCORING_PERIOD_ID = st.session_state.SCORING_PERIOD_ID
ESPN_S2 = st.session_state.ESPN_S2
SWID = st.session_state.SWID
ROSTER_DF = st.session_state.ROSTERS_DF



# --- Mapping of table numbers from each ranking type ---
table_numbers = {
    "sp_100_df": "4",
    "sh_100_df": "3",
    "hitters_150_df": "1",
}

# --- Load and Clean Ranking Data ---
rankings_dict = {}
for key, url in st.session_state.rankings_urls.items():
    try:
        table_num = table_numbers[key]
        df = get_pitcherlist_tables(url, table_num)
        df_cleaned = clean_players_names(df, "Player Names")
        merged_df = pd.merge(
            df_cleaned,
            ROSTER_DF[["Player Names", "Team Names"]],
            on="Player Names",
            how="left",
        )
        merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
        rankings_dict[key] = merged_df
    except Exception as e:
        st.error(f"Error loading {key}: {e}")

# --- Tab Labels ---
tab_labels = {
    "sp_100_df": "Top 100 SP",
    "sh_100_df": "Top 100 RP",
    "hitters_150_df": "Top 150 Hitters",
    "settings": "⚙️ Settings"
}

# --- Create Tabs ---
tabs = st.tabs([tab_labels[k] for k in rankings_dict.keys()] + [tab_labels["settings"]])

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
for i, key in enumerate(rankings_dict.keys()):
    with tabs[i]:
        st.subheader(tab_labels[key])
        df = rankings_dict[key]
        filtered_df = filter_dataframe(df, key)

        st.dataframe(filtered_df, use_container_width=True)

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {tab_labels[key]} CSV",
            data=csv_data,
            file_name=f"{tab_labels[key].replace(' ', '_')}.csv",
            mime="text/csv",
        )

# --- Settings Tab ---
with tabs[-1]:
    st.header("⚙️ Update PitcherList URLs")



    for key, label in zip(["sp_100_df", "sh_100_df", "hitters_150_df"], ["Top 100 SP URL", "Top 100 RP URL", "Top 150 Hitters URL"]):
        st.session_state.rankings_urls[key] = st.text_input(
            label=label, 
            value=st.session_state.rankings_urls[key], 
            key=f"url_input_{key}"
        )

    if st.button("Save Updated URLs"):
        with open(URLS_FILE, "w") as f:
            json.dump(st.session_state.rankings_urls, f, indent=4)
        st.success("URLs saved! They will persist next time you run the dashboard.")

    st.write("Current URLs:")
    for key, url in st.session_state.rankings_urls.items():
        st.write(f"{key}: {url}")
