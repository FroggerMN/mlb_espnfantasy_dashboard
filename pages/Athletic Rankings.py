import logging
import os
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.rankings_utilities import clean_players_names
from components.layout import page_scaffold, spacer
from components.tables import data_table
from components.empty_states import no_data_card
from components.filters import filter_dataframe
from components.charts import plotly_card

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
PAGE_TITLE = "Athletic Pitching Report"
EXCEL_PATH = "data/googlesheets/Pitch Report 2026.xlsx"
SESSION_STATE_ROSTER_KEY = "ROSTERS_DF"

@st.cache_data
def load_pitch_report() -> pd.DataFrame:
    """Loads and processes the Pitch Report Excel file."""
    try:
        df = pd.read_excel(EXCEL_PATH)
        # Rename 'Name' to 'Player Names'
        if 'Name' in df.columns:
            df = df.rename(columns={'Name': 'Player Names'})
            
        # Clean player names for matching
        df = clean_players_names(df, "Player Names")
        
        return df
    except Exception as e:
        logger.error(f"Error loading Pitch Report: {e}")
        st.error(f"Failed to load Pitch Report: {e}")
        return pd.DataFrame()

def process_rosters(df: pd.DataFrame, roster_df: pd.DataFrame) -> pd.DataFrame:
    """Merges pitcher data with roster data to assign fantasy teams."""
    if df.empty or roster_df.empty:
        return df
        
    merged_df = pd.merge(
        df,
        roster_df[["Player Names", "Team Names"]],
        on="Player Names",
        how="left",
    )
    
    merged_df["Team Names"] = merged_df["Team Names"].fillna("Available")
    
    # Move Team Names to the front
    cols = ["Player Names", "Team Names"] + [c for c in merged_df.columns if c not in ["Player Names", "Team Names"]]
    return merged_df[cols]

def render_visualizations(df: pd.DataFrame):
    """Renders the required plots for pitching analysis."""
    st.markdown("### Pitching Analysis")
    st.markdown("Use the plots below to analyze underlying predictive metrics. 100 is typically average for Stuff/Location+.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Stuff+ vs Location+
        if "Stuff+" in df.columns and "Location+" in df.columns and "Pitching+" in df.columns:
            plot_df = df.dropna(subset=["Stuff+", "Location+", "Pitching+"])
            if not plot_df.empty:
                fig1 = px.scatter(
                    plot_df, 
                    x="Stuff+", 
                    y="Location+", 
                    color="Pitching+",
                    hover_data=["Player Names", "Team Names"],
                    title="Stuff+ vs Location+",
                    color_continuous_scale="Viridis"
                )
                fig1.add_hline(y=100, line_dash="dash", line_color="red", opacity=0.5)
                fig1.add_vline(x=100, line_dash="dash", line_color="red", opacity=0.5)
                plotly_card(fig1, key="stuff_vs_location")
            
        # 3. Pitching+ vs Health
        if "Pitching+" in df.columns and "Health" in df.columns:
            plot_df3 = df.dropna(subset=["Pitching+", "Health"])
            if not plot_df3.empty:
                fig3 = px.scatter(
                    plot_df3,
                    x="Pitching+",
                    y="Health",
                    color="Team Names",
                    hover_data=["Player Names"],
                    title="Risk Assessment: Pitching+ vs Health"
                )
                plotly_card(fig3, key="pitching_vs_health")

    with col2:
        # 2. ppERA vs 26 ERA (Volatility/Regression)
        if "ppERA" in df.columns and "26 ERA" in df.columns:
            plot_df2 = df.dropna(subset=["ppERA", "26 ERA"])
            if not plot_df2.empty:
                fig2 = px.scatter(
                    plot_df2,
                    x="26 ERA",
                    y="ppERA",
                    color="Team Names",
                    hover_data=["Player Names"],
                    title="Regression Candidates (26 ERA vs ppERA)"
                )
                # Add y=x line
                min_val = min(plot_df2["26 ERA"].min(), plot_df2["ppERA"].min())
                max_val = max(plot_df2["26 ERA"].max(), plot_df2["ppERA"].max())
                fig2.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
                plotly_card(fig2, key="era_regression")

def main():
    """Main Streamlit page logic."""
    page_scaffold(
        PAGE_TITLE,
        "Evaluate pitching models and predictive stats (Stuff+, Pitching+) to find underlying talent.",
        page_title="Pitch Report",
    )

    if SESSION_STATE_ROSTER_KEY not in st.session_state or st.session_state[SESSION_STATE_ROSTER_KEY].empty:
        no_data_card()
        return

    roster_df = st.session_state[SESSION_STATE_ROSTER_KEY]
    
    df = load_pitch_report()
    if df.empty:
        return

    merged_df = process_rosters(df, roster_df)
    
    # UI Filter
    filtered_df = filter_dataframe(merged_df, key_prefix="pitch_report")
    
    spacer(8)
    
    # Table
    st.markdown("### Pitcher Rankings & Stats")
    filtered_df, selected_rows = data_table(filtered_df, key_prefix="pitch_report_table", enable_selection=True)
    
    spacer(8)
    
    # Filter for plots if rows are selected
    if selected_rows:
        plot_df = filtered_df.iloc[selected_rows]
    else:
        plot_df = filtered_df
    
    # Plots
    render_visualizations(plot_df)

if __name__ == "__main__":
    main()
