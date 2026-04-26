"""
components/filters.py

Filterable dataframe UI widget.
Moved from ``utils/ui.py`` to keep the component library self-contained.
"""

import logging

import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

logger = logging.getLogger(__name__)

# Default fantasy team name to pre-select in Team Names filters
_DEFAULT_MY_TEAM = "RP's, We Have Da Heat"


def filter_dataframe(
    df: pd.DataFrame,
    key_prefix: str,
    default_team: str = _DEFAULT_MY_TEAM,
) -> pd.DataFrame:
    """
    Renders an optional filter UI above a dataframe and returns the filtered result.

    Columns with fewer than 15 unique values get a multiselect widget.
    Numeric columns get a range slider.
    Object columns that look like dates are converted before filtering.

    Args:
        df:           The DataFrame to filter.
        key_prefix:   A unique string prefix for Streamlit widget keys (avoids
                      DuplicateWidgetID errors when multiple tables are on the same page).
        default_team: The fantasy team name to pre-select in "Team Names" filters.

    Returns:
        The filtered DataFrame (a copy; the original is not mutated).

    Example::

        filtered = filter_dataframe(rankings_df, key_prefix="sp100")
        st.dataframe(filtered)
    """
    modify = st.checkbox("Enable filters", value=True, key=f"{key_prefix}_filter_toggle")
    if not modify:
        return df

    df_filtered = df.copy()

    # --- Attempt date parsing on object columns ---
    for col in df_filtered.columns:
        if is_object_dtype(df_filtered[col]):
            try:
                df_filtered[col] = pd.to_datetime(df_filtered[col], format="%m/%d/%Y")
            except Exception:
                pass
        elif is_datetime64_any_dtype(df_filtered[col]):
            if df_filtered[col].dt.tz is not None:
                df_filtered[col] = df_filtered[col].dt.tz_localize(None)

    # --- Filter bar container ---
    st.markdown(
        '<div class="notion-filter-bar"><p class="filter-label">Filters</p>',
        unsafe_allow_html=True,
    )

    # --- Column selector ---
    to_filter_columns = st.multiselect(
        "Filter on columns",
        df_filtered.columns,
        default=["Team Names"] if "Team Names" in df_filtered.columns else None,
        key=f"{key_prefix}_filter_columns",
        label_visibility="collapsed",
    )

    # --- Per-column filter widgets ---
    if to_filter_columns:
        filter_cols = st.columns(min(len(to_filter_columns), 3))
        for idx, column in enumerate(to_filter_columns):
            col_container = filter_cols[idx % len(filter_cols)]
            unique_vals = df_filtered[column].unique()

            with col_container:
                if df_filtered[column].nunique() < 15:
                    # Categorical / low-cardinality → multiselect
                    if column == "Team Names":
                        default_vals = [v for v in [default_team, "Available"] if v in unique_vals]
                    else:
                        default_vals = list(unique_vals)

                    user_vals = st.multiselect(
                        f"{column}",
                        list(unique_vals),
                        default=default_vals,
                        key=f"{key_prefix}_{column}_select",
                    )
                    df_filtered = df_filtered[df_filtered[column].isin(user_vals)]

                elif is_numeric_dtype(df_filtered[column]):
                    # Numeric → range slider
                    try:
                        min_val = float(df_filtered[column].min())
                        max_val = float(df_filtered[column].max())
                        selected_range = st.slider(
                            f"{column}",
                            min_val,
                            max_val,
                            (min_val, max_val),
                            key=f"{key_prefix}_{column}_slider",
                        )
                        df_filtered = df_filtered[df_filtered[column].between(*selected_range)]
                    except Exception as exc:
                        logger.warning("Could not create slider for column %s: %s", column, exc)

    st.markdown("</div>", unsafe_allow_html=True)

    return df_filtered
