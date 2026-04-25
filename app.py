import logging
import pandas as pd
import streamlit as st

from data.fetch_espn_data import fetch_and_save_view
from data.espn_mlb_utilities import get_roster_info, get_category_stats, get_standings_table
from utils.logging_config import configure_logging
from utils.ui import (
    inject_notion_css,
    notion_page_header,
    notion_section_header,
    notion_card_begin,
    notion_card_end,
    notion_badge,
    notion_spacer,
)

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_YEAR = 2026
DEFAULT_LEAGUE_ID = 64175
DEFAULT_SCORING_PERIOD_WEEK = 2


def week_to_scoring_period(week: int) -> int:
    """Converts a fantasy week number to the ESPN scoring period ID (first day of that week)."""
    return week * 7 + 1


def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    session_defaults = {
        "YEAR": DEFAULT_YEAR,
        "LEAGUE_ID": DEFAULT_LEAGUE_ID,
        "SCORING_PERIOD_WEEK": DEFAULT_SCORING_PERIOD_WEEK,
        "ESPN_S2": "",
        "SWID": "",
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    # Always derive SCORING_PERIOD_ID from the current week
    st.session_state["SCORING_PERIOD_ID"] = week_to_scoring_period(
        st.session_state["SCORING_PERIOD_WEEK"]
    )


def render_config_panel():
    """Renders the league configuration panel in the main content area."""
    notion_section_header("League Configuration", "Set your league parameters and ESPN credentials to get started.")

    notion_card_begin()

    # Row 1: League settings
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.session_state.YEAR = st.number_input(
            "Year",
            value=st.session_state.YEAR,
            step=1,
            key="config_year",
        )
    with col2:
        st.session_state.LEAGUE_ID = st.number_input(
            "League ID",
            value=st.session_state.LEAGUE_ID,
            step=1,
            key="config_league_id",
        )
    with col3:
        selected_week = st.number_input(
            "Scoring Week",
            value=st.session_state.SCORING_PERIOD_WEEK,
            min_value=1,
            step=1,
            help="Select the fantasy week to analyze.",
            key="config_week",
        )
        if selected_week != st.session_state.SCORING_PERIOD_WEEK:
            st.session_state.SCORING_PERIOD_WEEK = selected_week
            st.session_state.SCORING_PERIOD_ID = week_to_scoring_period(selected_week)

    with col4:
        st.markdown(
            f'<p style="font-size:12px; color:#6F6F6F; text-transform:uppercase; '
            f'letter-spacing:0.04em; margin-bottom:4px;">Scoring Period ID</p>'
            f'<p style="font-size:22px; font-weight:600; color:#2F2F2F; margin:0;">'
            f'{st.session_state.SCORING_PERIOD_ID}</p>'
            f'<p style="font-size:12px; color:#9F9F9F; margin:0;">Week {st.session_state.SCORING_PERIOD_WEEK}</p>',
            unsafe_allow_html=True,
        )

    notion_spacer(12)

    # Row 2: Auth credentials
    with st.expander("Authentication Cookies", expanded=False):
        auth1, auth2 = st.columns(2)
        with auth1:
            st.session_state.ESPN_S2 = st.text_input(
                "ESPN_S2 Cookie",
                value=st.session_state.ESPN_S2,
                type="password",
                key="config_espn_s2",
            )
        with auth2:
            st.session_state.SWID = st.text_input(
                "SWID Cookie",
                value=st.session_state.SWID,
                type="password",
                key="config_swid",
            )

    notion_spacer(8)

    # Fetch button
    if st.button("Fetch Latest Data", key="fetch_data_btn"):
        fetch_and_process_data()

    notion_card_end()


def fetch_and_process_data():
    """Fetches ESPN data, processes the roster, and populates session state."""
    with st.spinner("Fetching data from ESPN..."):
        try:
            
            mTeam = fetch_and_save_view(
                st.session_state.YEAR,
                st.session_state.LEAGUE_ID,
                st.session_state.SCORING_PERIOD_ID,
                "mTeam",
                st.session_state.ESPN_S2,
                st.session_state.SWID
            )
            mRoster = fetch_and_save_view(
                st.session_state.YEAR,
                st.session_state.LEAGUE_ID,
                st.session_state.SCORING_PERIOD_ID,
                "mRoster",
                st.session_state.ESPN_S2,
                st.session_state.SWID
            )
            mBoxscore = fetch_and_save_view(
                st.session_state.YEAR,
                st.session_state.LEAGUE_ID,
                st.session_state.SCORING_PERIOD_ID,
                "mBoxscore",
                st.session_state.ESPN_S2,
                st.session_state.SWID
            )
            
            if mTeam and mRoster:
                rosters_df = get_roster_info(mRoster, mTeam)
                if not rosters_df.empty:
                    st.session_state.ROSTERS_DF = rosters_df
                    logger.info("ROSTERS_DF updated successfully.")
                else:
                    st.warning("Data fetched but roster output is empty.")
                    logger.warning("Empty dataframe returned by get_roster_info.")

                # Store mTeam for standings
                st.session_state.MTEAM_DATA = mTeam
                st.success("Data successfully fetched and rosters updated!")
            else:
                st.error("Failed to fetch mTeam or mRoster views. Check your ESPN cookies and IDs.")
                logger.error("Empty views returned from fetch_and_save_view.")
        except Exception as e:
            logger.exception(f"Unexpected error fetching data: {e}")
            st.error(f"An error occurred while fetching data: {e}")


def render_roster_status():
    """Renders the current roster data status card."""
    notion_section_header("Roster Data")

    notion_card_begin()
    if "ROSTERS_DF" in st.session_state and not st.session_state.ROSTERS_DF.empty:
        notion_badge("Loaded", "success")
        notion_spacer(12)
        st.dataframe(st.session_state.ROSTERS_DF, use_container_width=True, hide_index=True)
    else:
        notion_badge("Not loaded", "warning")
        notion_spacer(8)
        st.markdown(
            '<p style="font-size:14px; color:#6F6F6F;">Click <strong>Fetch Latest Data</strong> above to load roster data.</p>',
            unsafe_allow_html=True,
        )
    notion_card_end()


def render_standings_section():
    """Renders the league standings + season-to-date category stats table."""
    notion_section_header(
        "League Standings & Category Stats",
        "Season-to-date performance across all 10 scoring categories.",
    )

    mteam = st.session_state.get("MTEAM_DATA")
    if not mteam:
        notion_card_begin()
        st.markdown(
            '<p style="font-size:14px; color:#6F6F6F;">Standings not available. '
            'Click <strong>Fetch Latest Data</strong> above to load.</p>',
            unsafe_allow_html=True,
        )
        notion_card_end()
        return

    with st.spinner("Building standings table…"):
        cat_stats = get_category_stats(
            st.session_state.LEAGUE_ID,
            st.session_state.YEAR,
            st.session_state.SCORING_PERIOD_ID,
        )
        standings_df = get_standings_table(mteam, cat_stats)

    if standings_df.empty:
        st.warning("Could not build standings table. The mBoxscore JSON may not be available for this scoring period.")
        return

    notion_card_begin()

    # View mode toggle
    view_mode = st.radio(
        "View format",
        ["Stat Totals", "Z-Scores"],
        horizontal=True,
        label_visibility="collapsed",
    )

    notion_spacer(8)

    # --- Colour-code stat columns: green = top 3, red = bottom 3 ---
    from utils.config import TARGET_STATS, STATS_LOW_IS_BETTER
    stat_cols = [c for c in TARGET_STATS if c in standings_df.columns]
    
    display_df = standings_df.copy()
    if view_mode == "Z-Scores":
        for col in stat_cols:
            std = display_df[col].astype(float).std()
            if std != 0:
                display_df[col] = (display_df[col].astype(float) - display_df[col].astype(float).mean()) / std
                # For ERA and WHIP, invert the Z-score so positive is always better
                if col in STATS_LOW_IS_BETTER:
                    display_df[col] = -display_df[col]
            else:
                display_df[col] = 0.0

    def highlight_stats(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        for col in stat_cols:
            if col not in df.columns:
                continue
            # If Z-Scores view, positive is always better (we inverted ERA/WHIP above)
            is_low_better = (col in STATS_LOW_IS_BETTER) and (view_mode == "Stat Totals")
            ranks = df[col].rank(ascending=is_low_better, method="min", na_option="bottom")
            n = df[col].notna().sum()
            for idx in df.index:
                r = ranks[idx]
                if r <= 3:
                    styles.at[idx, col] = "background-color: #1a7a4a; color: white;"
                elif r > n - 3:
                    styles.at[idx, col] = "background-color: #8b1a1a; color: white;"
        return styles

    if view_mode == "Z-Scores":
        fmt = {c: "{:+.2f}" for c in stat_cols}
    else:
        fmt = {c: "{:.3f}" for c in stat_cols if c in {"AVG", "ERA", "WHIP"}}
        fmt.update({c: "{:.0f}" for c in stat_cols if c not in {"AVG", "ERA", "WHIP"}})
    
    # Format the component columns on the far right (always display as raw totals)
    component_cols = ["H", "AB", "ER", "IP", "BB", "HA"]
    for c in component_cols:
        if c in display_df.columns:
            if c == "IP":
                fmt[c] = "{:.1f}"
            else:
                fmt[c] = "{:.0f}"

    styled = display_df.style.apply(highlight_stats, axis=None).format(fmt)

    st.dataframe(styled, use_container_width=True, hide_index=True, height=460)
    st.caption(
        "Counting stats (R, HR, RBI, SB, K, W, SVHD) are season totals. "
        "Ratio stats (AVG, ERA, WHIP) are season-to-date, recalculated from component sums. "
        "Top 3 highlighted green · Bottom 3 highlighted red per category."
    )
    notion_card_end()


def main():
    """Main application logic for app.py."""
    configure_logging()  # Must be first — configures handlers for all child loggers
    st.set_page_config(page_title="MLB Fantasy Dashboard", layout="wide", page_icon="⚾")
    inject_notion_css()
    
    initialize_session_state()

    # --- Page Header ---
    notion_page_header(
        "MLB Fantasy Dashboard",
        "ESPN Fantasy Baseball API dashboard for your 12-team H2H league. "
        "Configure your league below, fetch data, then explore analysis pages from the sidebar.",
    )

    notion_spacer(8)

    # --- Getting Started (collapsed by default) ---
    with st.expander("Getting Started", expanded=False):
        st.markdown("""
1. Enter your league credentials below.
2. Click **Fetch Latest Data**.
3. Navigate to the analysis pages in the sidebar — *Athletic Rankings*, *Category Rolling Average*, *PitchersList Rankings*.
        """)

    notion_spacer(8)

    # --- League Configuration Panel (moved from sidebar) ---
    render_config_panel()

    # --- Roster Status ---
    render_roster_status()

    # --- Standings ---
    render_standings_section()


if __name__ == "__main__":
    main()
