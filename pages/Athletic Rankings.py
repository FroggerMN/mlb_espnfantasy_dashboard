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
from utils.ui import (
    inject_notion_css,
    notion_page_header,
    notion_card_begin,
    notion_card_end,
    notion_spacer,
    filter_dataframe,
)

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



def main():
    """Main Streamlit page logic."""
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    inject_notion_css()

    notion_page_header(
        PAGE_TITLE,
        "Player rankings sourced from The Athletic, cross-referenced with your roster.",
    )

    if SESSION_STATE_ROSTER_KEY not in st.session_state or st.session_state[SESSION_STATE_ROSTER_KEY].empty:
        notion_card_begin()
        st.markdown(
            '<p style="font-size:14px; color:#6F6F6F;">No roster data available. '
            'Return to the home page and click <strong>Fetch Latest Data</strong>.</p>',
            unsafe_allow_html=True,
        )
        notion_card_end()
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

    notion_spacer(8)
    tabs = st.tabs(list(rankings_dict.keys()))

    for i, (key, df) in enumerate(rankings_dict.items()):
        with tabs[i]:
            notion_spacer(8)
            filtered_df = filter_dataframe(df, key)
            notion_card_begin()
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            notion_card_end()


if __name__ == "__main__":
    main()
