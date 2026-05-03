import logging
import numpy as np

import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from data.espn_mlb_utilities import get_category_stats
from components.layout import page_scaffold, spacer
from components.typography import section_header
from components.charts import plotly_card
from components.filters import filter_dataframe
from components.empty_states import missing_config_card
from components._tokens import COLORS, PLOTLY_LAYOUT_DEFAULTS
from utils.config import TARGET_STATS

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
PAGE_TITLE = "Category Rolling Trends"
DEFAULT_MAX_WEEK = 14

@st.cache_data
def load_category_stats(league_id: int, year: int, scoring_period_id: int, max_week: int, rolling_window: int) -> pd.DataFrame:
    """Loads and processes category statistics."""
    try:
        df = get_category_stats(league_id, year, scoring_period_id)
        if df.empty:
            logger.warning("get_category_stats returned an empty DataFrame.")
            return df
            
        df = df[df['matchupPeriodId'] <= max_week]
        
        def compute_rolling(data_df, team_col):
            data_df = data_df.sort_values([team_col, "Stat Name", "matchupPeriodId"])
            ratio_stats = {"AVG", "ERA", "WHIP"}
            components = ["H", "AB", "ER", "OUTS", "P_BB", "P_H"]
            results = []
            
            grouped = data_df.groupby([team_col, "Stat Name"])
            for name, group in grouped:
                g = group.copy()
                stat = name[1]
                
                # Use sum for ratio stat calculations
                if stat in components:
                    g["Rolling_Sum"] = g["Score"].rolling(rolling_window, min_periods=1).sum()
                else:
                    g["Rolling_Sum"] = np.nan
                    
                # Use mean for everything else (for the charts)
                if stat not in ratio_stats:
                    g["Rolling_Value"] = g["Score"].rolling(rolling_window, min_periods=1).mean()
                else:
                    g["Rolling_Value"] = np.nan
                results.append(g)
                
            res_df = pd.concat(results, ignore_index=True)
            pivot = res_df.pivot_table(index=[team_col, "matchupPeriodId"], columns="Stat Name", values="Rolling_Sum").reset_index()
            
            if "H" in pivot.columns and "AB" in pivot.columns:
                pivot["AVG"] = (pivot["H"] / pivot["AB"]).replace([np.inf, -np.inf], 0).fillna(0)
            if "ER" in pivot.columns and "OUTS" in pivot.columns:
                pivot["ERA"] = ((pivot["ER"] / (pivot["OUTS"] / 3)) * 9).replace([np.inf, -np.inf], 0).fillna(0)
            if "P_BB" in pivot.columns and "P_H" in pivot.columns and "OUTS" in pivot.columns:
                pivot["WHIP"] = ((pivot["P_BB"] + pivot["P_H"]) / (pivot["OUTS"] / 3)).replace([np.inf, -np.inf], 0).fillna(0)
                
            melted = pivot.melt(id_vars=[team_col, "matchupPeriodId"], value_vars=[s for s in ratio_stats if s in pivot.columns], var_name="Stat Name", value_name="Calculated_Rolling")
            final_df = res_df.merge(melted, on=[team_col, "matchupPeriodId", "Stat Name"], how="left")
            final_df[f"Rolling_Ave({rolling_window})"] = final_df["Calculated_Rolling"].combine_first(final_df["Rolling_Value"])
            return final_df
        
        # 1. Individual Teams
        team_df = compute_rolling(df, "Team Names")
        
        # 2. League Average
        league_base = []
        for (period, stat), group in df.groupby(["matchupPeriodId", "Stat Name"]):
            val = group["Score"].mean()
            league_base.append({"Team Names": "League Average", "matchupPeriodId": period, "Stat Name": stat, "Score": val})
            
        league_rolling = compute_rolling(pd.DataFrame(league_base), "Team Names")
        
        final_df = pd.concat([team_df, league_rolling], ignore_index=True)
        
        # Add IP stat
        outs_df = final_df[final_df["Stat Name"] == "OUTS"].copy()
        if not outs_df.empty:
            outs_df["Stat Name"] = "IP"
            outs_df["Score"] = outs_df["Score"] / 3
            outs_df[f"Rolling_Ave({rolling_window})"] = outs_df[f"Rolling_Ave({rolling_window})"] / 3
            final_df = pd.concat([final_df, outs_df], ignore_index=True)
            
        logger.info(f"Successfully loaded category stats up to week {max_week}.")
        return final_df
    except Exception as e:
        logger.error(f"Error loading category stats: {e}")
        st.error("Failed to load category statistics. See logs for details.")
        return pd.DataFrame()



def render_plots(df: pd.DataFrame, filtered_df: pd.DataFrame, rolling_window: int):
    """Renders the Plotly charts for each statistic category using plotly_card."""
    display_stats = TARGET_STATS + ["AB", "H", "IP"]
    stat_categories = [s for s in display_stats if s in df["Stat Name"].unique()]

    # Render in a 2-column grid
    cols = st.columns(2)

    for idx, stat in enumerate(stat_categories):
        stat_df = filtered_df[filtered_df["Stat Name"] == stat]
        if stat_df.empty:
            continue

        fig = go.Figure()

        # Get teams (excluding League Average)
        teams = [t for t in stat_df["Team Names"].unique() if t != "League Average"]

        for team in teams:
            team_data = stat_df[stat_df["Team Names"] == team]
            fig.add_trace(go.Scatter(
                x=team_data["matchupPeriodId"],
                y=team_data[f"Rolling_Ave({rolling_window})"],
                mode="lines+markers",
                name=team,
                line=dict(width=2),
                marker=dict(size=5),
            ))

        # Add League Average line
        if "League Average" in stat_df["Team Names"].values:
            league_data = stat_df[stat_df["Team Names"] == "League Average"]
            fig.add_trace(go.Scatter(
                x=league_data["matchupPeriodId"],
                y=league_data[f"Rolling_Ave({rolling_window})"],
                mode="lines",
                name="League Average",
                line=dict(width=3, color="#D97706", dash="dash"),
            ))

        fig.update_layout(
            title=dict(text=f"{stat} — {rolling_window}-Week Rolling Avg", font=dict(size=15, color=COLORS["text_primary"])),
            showlegend=True,
            xaxis=dict(title="Matchup Period", dtick=1),
        )

        with cols[idx % 2]:
            plotly_card(fig, key=f"chart_{stat}_{idx}")


def main():
    """Main Streamlit page logic."""
    page_scaffold(
        PAGE_TITLE,
        "Track 3-week rolling averages across all scoring categories for each team.",
        page_title="Categories",
    )

    # --- League Info ---
    required_keys = ["YEAR", "LEAGUE_ID", "SCORING_PERIOD_ID"]
    if any(k not in st.session_state for k in required_keys):
        missing_config_card()
        return

    year = st.session_state.YEAR
    league_id = st.session_state.LEAGUE_ID
    scoring_period_id = st.session_state.SCORING_PERIOD_ID
    max_week_to_show = st.session_state.get("SCORING_PERIOD_WEEK", DEFAULT_MAX_WEEK) - 1

    # Add rolling window configuration
    max_rolling_window = max(1, max_week_to_show - 2)
    
    spacer(4)
    col1, _ = st.columns([1, 3])
    with col1:
        rolling_window = st.number_input(
            "Rolling Average Window (Weeks)",
            min_value=1,
            max_value=max_rolling_window,
            value=min(3, max_rolling_window),
            step=1,
        )

    df = load_category_stats(league_id, year, scoring_period_id, max_week_to_show, rolling_window)
    
    if df.empty:
        st.warning("No category data available to display.")
        return

    spacer(8)
    filtered_df = filter_dataframe(df, key_prefix="category_rolling")

    # --- Download Option ---
    spacer(4)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "category_trends.csv", "text/csv")

    spacer(8)

    # --- Plot ---
    render_plots(df, filtered_df, rolling_window)


if __name__ == "__main__":
    main()

