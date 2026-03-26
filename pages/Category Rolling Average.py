# pages/Category Rolling Average.py

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from data.espn_mlb_utilities import get_category_stats
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype, is_object_dtype

# --- Page Setup ---
st.set_page_config(page_title="Categories", layout="wide")
st.title("📈 Category Rolling Trends")

# --- League Info ---
YEAR = st.session_state.YEAR
LEAGUE_ID = st.session_state.LEAGUE_ID
SCORING_PERIOD_ID = st.session_state.SCORING_PERIOD_ID
MAX_WEEK_TO_SHOW = st.session_state.get("SCORING_PERIOD_WEEK", 14)-1 # Default to 14 if not set

# --- Load Data ---
# Load Data
# Load Data
@st.cache_data
def load_category_stats(max_week): # Add max_week parameter
    df = get_category_stats(LEAGUE_ID, YEAR, SCORING_PERIOD_ID)
    # Filter data to include only weeks up to max_week
    df = df[df['matchupPeriodId'] <= max_week] # <--- ADD THIS FILTERING LINE
    df = df.sort_values(["Stat Name", "Team Names", "matchupPeriodId"])
    df["Rolling_Ave(3)"] = df.groupby(["Stat Name", "Team Names"])["Score"].transform(
        lambda x: x.rolling(3, min_periods=3).mean()
    )
    return df

df = load_category_stats(MAX_WEEK_TO_SHOW)

# --- Filter Control ---
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not st.checkbox("Filter DataFrame", value=True):
        return df

    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format='%m/%d/%Y')
            except Exception:
                pass
        elif is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    filter_cols = st.multiselect("Filter by", df.columns, default=["Team Names"])
    for col in filter_cols:
        if df[col].nunique() < 15:
            default = ["RP's, We Have Da Heat"] if col == "Team Names" else list(df[col].unique())
            selected = st.multiselect(f"{col}", df[col].unique(), default=default)
            df = df[df[col].isin(selected)]
        elif is_numeric_dtype(df[col]):
            min_val, max_val = float(df[col].min()), float(df[col].max())
            df = df[df[col].between(*st.slider(f"{col} range", min_val, max_val, (min_val, max_val)))]

    return df

filtered_df = filter_dataframe(df)

# --- Download Option ---
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "category_trends.csv", "text/csv")

# --- Plot ---
stat_categories = sorted(df["Stat Name"].unique())

for stat in stat_categories:
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
            name=team
        ))

    # Add benchmark lines
    try:
        stat_ave = stat_df["Stat Ave"].iloc[0]
        stat_win_ave = stat_df["Stat Win Ave"].iloc[0]
        x_min, x_max = stat_df["matchupPeriodId"].min(), stat_df["matchupPeriodId"].max()

        fig.add_shape(type="line", x0=x_min, x1=x_max, y0=stat_ave, y1=stat_ave,
                      line=dict(color="red", dash="dash"))
        fig.add_annotation(x=x_max, y=stat_ave, text=f"Stat Ave: {stat_ave:.2f}",
                           showarrow=False, yshift=10, font=dict(color="red"))

        fig.add_shape(type="line", x0=x_min, x1=x_max, y0=stat_win_ave, y1=stat_win_ave,
                      line=dict(color="green", dash="dash"))
        fig.add_annotation(x=x_max, y=stat_win_ave, text=f"Win Ave: {stat_win_ave:.2f}",
                           showarrow=False, yshift=-10, font=dict(color="green"))
    except IndexError:
        pass

    fig.update_layout(
        title=f"{stat} — 3-week Rolling Avg",
        xaxis_title="Matchup Period",
        yaxis_title=stat,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)


