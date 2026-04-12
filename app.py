import logging
import streamlit as st

from data.fetch_espn_data import fetch_and_save_view
from data.espn_mlb_utilities import get_roster_info
from utils.logging_config import configure_logging

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_YEAR = 2026
DEFAULT_LEAGUE_ID = 64175
DEFAULT_SCORING_PERIOD_ID = 1
DEFAULT_SCORING_PERIOD_WEEK = 14

def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    session_defaults = {
        "YEAR": DEFAULT_YEAR,
        "LEAGUE_ID": DEFAULT_LEAGUE_ID,
        "SCORING_PERIOD_ID": DEFAULT_SCORING_PERIOD_ID,
        "SCORING_PERIOD_WEEK": DEFAULT_SCORING_PERIOD_WEEK,
        "ESPN_S2": "",
        "SWID": "",
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_sidebar():
    """Renders the sidebar for configuring league settings."""
    st.sidebar.header("League Settings")
    
    st.session_state.YEAR = st.sidebar.number_input(
        "Year", 
        value=st.session_state.YEAR, 
        step=1
    )
    st.session_state.LEAGUE_ID = st.sidebar.number_input(
        "League ID", 
        value=st.session_state.LEAGUE_ID, 
        step=1
    )
    st.session_state.SCORING_PERIOD_ID = st.sidebar.number_input(
        "Scoring Period ID", 
        value=st.session_state.SCORING_PERIOD_ID, 
        step=1,
        help="The specific period to fetch ESPN json views for."
    )
    st.session_state.SCORING_PERIOD_WEEK = st.sidebar.number_input(
        "Max Matchup Week", 
        value=st.session_state.SCORING_PERIOD_WEEK, 
        step=1,
        help="Used to filter charts in the Category Rolling Average page."
    )
    
    st.sidebar.subheader("Authentication Cookies")
    st.session_state.ESPN_S2 = st.sidebar.text_input(
        "ESPN_S2 Cookie", 
        value=st.session_state.ESPN_S2, 
        type="password"
    )
    st.session_state.SWID = st.sidebar.text_input(
        "SWID Cookie", 
        value=st.session_state.SWID, 
        type="password"
    )

    if st.sidebar.button("Fetch Latest Data"):
        fetch_and_process_data()


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
                    st.success("Data successfully fetched and rosters updated!")
                    logger.info("ROSTERS_DF updated successfully.")
                else:
                    st.warning("Data fetched but roster output is empty.")
                    logger.warning("Empty dataframe returned by get_roster_info.")
            else:
                st.error("Failed to fetch mTeam or mRoster views. Check your ESPN cookies and IDs.")
                logger.error("Empty views returned from fetch_and_save_view.")
        except Exception as e:
            logger.exception(f"Unexpected error fetching data: {e}")
            st.error(f"An error occurred while fetching data: {e}")


def main():
    """Main application logic for app.py."""
    configure_logging()  # Must be first — configures handlers for all child loggers
    st.set_page_config(page_title="MLB Fantasy Dashboard", layout="wide", page_icon="⚾")
    
    initialize_session_state()
    render_sidebar()
    
    st.title("⚾ MLB Fantasy Dashboard")
    st.markdown("""
        Welcome to the **MLB Fantasy Dashboard**! 
        
        This dashboard uses the ESPN Fantasy Baseball API to manage your 12-team Head-to-Head (H2H) league. 
        Use the sidebar to configure your league ID, Year, Authentication cookies (SWID/ESPN_s2), and the particular Scoring Period you want to analyze.
        
        ### Getting Started
        1. Fill in your credentials on the sidebar.
        2. Click **Fetch Latest Data**.
        3. Navigate to the pages on the left (e.g., *Athletic Rankings*, *Category Rolling Average*, etc.) for specific analyses based on your current rosters.
        
        ### Current Roster Data Status
    """)
    
    if "ROSTERS_DF" in st.session_state and not st.session_state.ROSTERS_DF.empty:
        st.success("✅ Roster Data is currently loaded in the session state!")
        st.dataframe(st.session_state.ROSTERS_DF, width='stretch')
    else:
        st.warning("⚠️ Roster Data has not been loaded. Please hit **Fetch Latest Data** on the sidebar.")


if __name__ == "__main__":
    main()
