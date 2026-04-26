import logging

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

# --- Initialize logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
PAGE_TITLE = "Category Rolling Trends"
DEFAULT_MAX_WEEK = 14

@st.cache_data
def load_category_stats(league_id: int, year: int, scoring_period_id: int, max_week: int) -> pd.DataFrame:
    """Loads and processes category statistics."""
    try:
        df = get_category_stats(league_id, year, scoring_period_id)
        if df.empty:
            logger.warning("get_category_stats returned an empty DataFrame.")
            return df
            
        df = df[df['matchupPeriodId'] <= max_week]
        df = df.sort_values(["Stat Name", "Team Names", "matchupPeriodId"])
        df["Rolling_Ave(3)"] = df.groupby(["Stat Name", "Team Names"])["Score"].transform(
            lambda x: x.rolling(3, min_periods=3).mean()
        )
        logger.info(f"Successfully loaded category stats up to week {max_week}.")
        return df
    except Exception as e:
        logger.error(f"Error loading category stats: {e}")
        st.error("Failed to load category statistics. See logs for details.")
        return pd.DataFrame()



def render_plots(df: pd.DataFrame, filtered_df: pd.DataFrame):
    """Renders the Plotly charts for each statistic category using plotly_card."""
    stat_categories = sorted(df["Stat Name"].unique())

    # Render in a 2-column grid
    cols = st.columns(2)

    for idx, stat in enumerate(stat_categories):
        stat_df = filtered_df[filtered_df["Stat Name"] == stat]
        if stat_df.empty:
            continue

        fig = go.Figure()

        for team in stat_df["Team Names"].unique():
            team_data = stat_df[stat_df["Team Names"] == team]
            fig.add_trace(go.Scatter(
                x=team_data["matchupPeriodId"],
                y=team_data["Rolling_Ave(3)"],
                mode="lines+markers",
                name=team,
                line=dict(width=2),
                marker=dict(size=5),
            ))

        # Add benchmark lines
        try:
            stat_ave = stat_df["Stat Ave"].iloc[0]
            stat_win_ave = stat_df["Stat Win Ave"].iloc[0]
            x_min, x_max = stat_df["matchupPeriodId"].min(), stat_df["matchupPeriodId"].max()

            fig.add_shape(type="line", x0=x_min, x1=x_max, y0=stat_ave, y1=stat_ave,
                          line=dict(color="#D97706", dash="dash", width=1.5))
            fig.add_annotation(x=x_max, y=stat_ave, text=f"Avg: {stat_ave:.2f}",
                               showarrow=False, yshift=10, font=dict(color="#D97706", size=11))

            fig.add_shape(type="line", x0=x_min, x1=x_max, y0=stat_win_ave, y1=stat_win_ave,
                          line=dict(color="#059669", dash="dash", width=1.5))
            fig.add_annotation(x=x_max, y=stat_win_ave, text=f"Win: {stat_win_ave:.2f}",
                               showarrow=False, yshift=-10, font=dict(color="#059669", size=11))
        except IndexError:
            logger.debug(f"Missing benchmark data for stat: {stat}")
        except Exception as e:
            logger.warning(f"Error drawing benchmarks for stat {stat}: {e}")

        fig.update_layout(
            title=dict(text=f"{stat} — 3-Week Rolling Avg", font=dict(size=15, color=COLORS["text_primary"])),
            showlegend=True,
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

    df = load_category_stats(league_id, year, scoring_period_id, max_week_to_show)
    
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
    render_plots(df, filtered_df)


if __name__ == "__main__":
    main()

