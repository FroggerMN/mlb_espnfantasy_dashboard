import json
import logging
import os
from typing import Dict

import pandas as pd
import streamlit as st

from data.fetch_pitcherlist_ranking import get_pitcherlist_tables
from data.fetch_pitcherlist_sitstart import fetch_sit_start_data
from utils.rankings_utilities import clean_players_names
from utils.ui import (
    inject_notion_css,
    notion_page_header,
    notion_section_header,
    notion_card_begin,
    notion_card_end,
    notion_spacer,
    filter_dataframe,
)

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
URLS_FILE = "data/pitcherslist_urls.json"
PAGE_TITLE = "PitchersList Rankings"

TABLE_NUMBERS = {
    "sp_100_df": 0,
    "sh_100_df": 2,  # 3rd valid table (SV+HLD)
    "hitters_150_df": 0,
    "sit_start_df": -1,
}

TAB_LABELS = {
    "sp_100_df": "Top 100 SP",
    "sh_100_df": "Top 100 RP",
    "hitters_150_df": "Top 150 Hitters",
    "sit_start_df": "Start / Sit",
    "settings": "Settings"
}

def load_urls() -> Dict[str, str]:
    """Load URLs from file if available, otherwise use defaults."""
    if os.path.exists(URLS_FILE):
        try:
            with open(URLS_FILE, "r") as f:
                logger.info(f"Loaded URLs from {URLS_FILE}")
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {URLS_FILE}: {e}")
        except Exception as e:
            logger.error(f"Error reading {URLS_FILE}: {e}")

    logger.info("Using default PitchersList URLs.")
    return {
        "sp_100_df": "https://pitcherlist.com/top-100-starting-pitchers-for-2025-fantasy-baseball-week-8-5-19/",
        "sh_100_df": "https://pitcherlist.com/rp-ranks-5-23-the-top-100-relievers-for-savehold-leagues//",
        "hitters_150_df": "https://pitcherlist.com/top-150-hitters-for-fantasy-baseball-2025-week-8-5-22/",
        "sit_start_df": "https://pitcherlist.com/sit-start-week-1-reviewing-all-starting-pitcher-matchups-from-3-30-4-5/",
    }

def fetch_and_clean_rankings(urls: Dict[str, str], roster_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Fetches ranking data, cleans names, and merges with roster."""
    rankings_dict = {}
    for key, url in urls.items():
        try:
            if key == "sit_start_df":
                df = fetch_sit_start_data(url)
                if df.empty:
                    logger.warning("Returned empty sit/start dataframe.")
                    continue
                # For sit_start, names are "FirstInitial. Lastname"
                df_cleaned = clean_players_names(df, "Player Names")
                
                # We need to create a matching key on the roster side that matches "F. Lastname"
                from utils.rankings_utilities import full_name_2_initial_last
                
                roster_for_join = roster_df[["Player Names", "Team Names"]].copy()
                roster_for_join["Player Names Cleaned"] = clean_players_names(roster_df, "Player Names")["Player Names"]
                roster_for_join["Match Name"] = roster_for_join["Player Names Cleaned"].apply(full_name_2_initial_last)
                
                # In df_cleaned, "Player Names" is already in the F. Lastname format (and cleaned)
                # But sometimes PitcherList includes middle initials. A robust regex clean could be done, 
                # but let's assume `clean_players_names` handles basics and we match using `Match Name`.
                
                # We merge on Match Name, bringing over the ESPN Full Name and Fantasy Team
                merged_df = pd.merge(
                    df_cleaned, 
                    roster_for_join, 
                    left_on="Player Names", 
                    right_on="Match Name", 
                    how="left"
                )
                
                # Replace the short name with the ESPN full name where we matched one
                merged_df["Player Names"] = merged_df["Player Names_y"].fillna(merged_df["Player Names_x"])
                
                # Clean up auxiliary columns
                merged_df = merged_df.drop(columns=["Player Names_x", "Player Names_y", "Player Names Cleaned", "Match Name"], errors='ignore')
                
                merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
                merged_df = merged_df.sort_values(by="Team Names").reset_index(drop=True)
                rankings_dict[key] = merged_df
            else:
                table_num = TABLE_NUMBERS.get(key)
                if table_num is None:
                    logger.warning(f"No table number found for key {key}")
                    continue
                df = get_pitcherlist_tables(url, table_num)
                df_cleaned = clean_players_names(df, "Player Names")
                merged_df = pd.merge(
                    df_cleaned,
                    roster_df[["Player Names", "Team Names"]],
                    on="Player Names",
                    how="left",
                )
                merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
                rankings_dict[key] = merged_df
            
            logger.info(f"Successfully loaded and cleaned data for {key}")
        except Exception as e:
            logger.error(f"Error loading {key} from {url}: {e}")
            st.error(f"Error loading {TAB_LABELS.get(key, key)}: {e}")
            
    return rankings_dict

def render_settings_tab():
    """Renders the settings tab to update the URLs."""
    notion_section_header("Update PitcherList URLs", "Change the source URLs for each ranking table.")

    notion_card_begin()

    keys = ["sp_100_df", "sh_100_df", "hitters_150_df", "sit_start_df"]
    labels = ["Top 100 SP URL", "Top 100 RP URL", "Top 150 Hitters URL", "Start / Sit URL"]

    for key, label in zip(keys, labels):
        st.session_state.rankings_urls[key] = st.text_input(
            label=label, 
            value=st.session_state.rankings_urls.get(key, ""), 
            key=f"url_input_{key}"
        )

    notion_spacer(8)

    if st.button("Save Updated URLs"):
        try:
            with open(URLS_FILE, "w") as f:
                json.dump(st.session_state.rankings_urls, f, indent=4)
            st.success("URLs saved! They will persist next time you run the dashboard.")
            logger.info(f"Successfully saved updated URLs to {URLS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save URLs: {e}")
            st.error(f"Failed to save URLs: {e}")

    notion_card_end()

    notion_spacer(16)

    # Display current URLs
    notion_card_begin("Current URLs")
    for key, url in st.session_state.rankings_urls.items():
        st.markdown(
            f'<p style="margin:4px 0;"><span style="font-size:12px; color:#6F6F6F; '
            f'text-transform:uppercase; letter-spacing:0.04em;">{TAB_LABELS.get(key, key)}</span><br/>'
            f'<span style="font-size:13px; color:#2F2F2F; word-break:break-all;">{url}</span></p>',
            unsafe_allow_html=True,
        )
    notion_card_end()


def main():
    """Main Streamlit page logic."""
    st.set_page_config(page_title="PitchersList SP100", layout="wide")
    inject_notion_css()

    notion_page_header(
        PAGE_TITLE,
        "Rankings from PitcherList.com, cross-referenced with your ESPN roster.",
    )

    # Ensure URLs are loaded into session state
    if "rankings_urls" not in st.session_state:
        st.session_state.rankings_urls = load_urls()

    if "ROSTERS_DF" not in st.session_state or st.session_state["ROSTERS_DF"].empty:
        notion_card_begin()
        st.markdown(
            '<p style="font-size:14px; color:#6F6F6F;">No roster data available. '
            'Return to the home page and click <strong>Fetch Latest Data</strong>.</p>',
            unsafe_allow_html=True,
        )
        notion_card_end()
        return
        
    roster_df = st.session_state["ROSTERS_DF"]

    rankings_dict = fetch_and_clean_rankings(st.session_state.rankings_urls, roster_df)

    # Prepare tab layout
    valid_keys = list(rankings_dict.keys())
    tab_names = [TAB_LABELS[k] for k in valid_keys] + [TAB_LABELS["settings"]]
    
    if tab_names:
        notion_spacer(8)
        tabs = st.tabs(tab_names)

        # Render ranking tabs
        for i, key in enumerate(valid_keys):
            with tabs[i]:
                notion_spacer(8)
                df = rankings_dict[key]
                filtered_df = filter_dataframe(df, key)

                notion_card_begin()
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)

                notion_spacer(8)
                csv_data = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"Download {TAB_LABELS[key]} CSV",
                    data=csv_data,
                    file_name=f"{TAB_LABELS[key].replace(' ', '_')}.csv",
                    mime="text/csv",
                )
                notion_card_end()

        # Render settings tab (the last tab)
        with tabs[-1]:
            notion_spacer(8)
            render_settings_tab()
    else:
        st.warning("No rendering tabs available.")

if __name__ == "__main__":
    main()
