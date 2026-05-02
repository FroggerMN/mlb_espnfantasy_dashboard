"""
utils/ui.py

Shared Streamlit UI components used across multiple dashboard pages.
Centralising these avoids code duplication and ensures consistent behaviour.

Notion-style design system helpers included.
"""

import logging
from pathlib import Path

import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

logger = logging.getLogger(__name__)

# Default fantasy team names to pre-select in Team Names filters
_DEFAULT_MY_TEAM = "RP's, We Have Da Heat"

# --- Notion-style design tokens (mirrored from CSS for Plotly etc.) ---
NOTION_COLORS = {
    "bg_primary": "#FAFAF8",
    "bg_card": "#FFFFFF",
    "bg_filter": "#F5F5F3",
    "border": "#E5E5E0",
    "text_primary": "#2F2F2F",
    "text_secondary": "#6F6F6F",
    "text_muted": "#9F9F9F",
    "accent": "#5B8A9A",
    "accent_hover": "#4A7585",
    "accent_light": "#EBF3F6",
    "grid": "#EDEDEA",
}

PLOTLY_LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", color="#2F2F2F", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    xaxis=dict(gridcolor="#EDEDEA", linecolor="#E5E5E0", zeroline=False),
    yaxis=dict(gridcolor="#EDEDEA", linecolor="#E5E5E0", zeroline=False),
    margin=dict(l=48, r=24, t=48, b=40),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
)


# ============================================================
# CSS Injection
# ============================================================

def inject_notion_css():
    """Loads and injects the Notion design system CSS into the Streamlit page."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    try:
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        logger.warning("Could not find assets/styles.css — Notion CSS not loaded.")


# ============================================================
# Page Header
# ============================================================

def notion_page_header(title: str, description: str = ""):
    """Renders a clean Notion-style page header with optional description."""
    html = f'<div class="notion-page-header"><h1>{title}</h1>'
    if description:
        html += f'<p class="notion-page-header-desc">{description}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# Section Header
# ============================================================

def notion_section_header(title: str, description: str = ""):
    """Renders a Notion-style section header (H2 + optional subtitle)."""
    html = f'<div class="notion-section"><h2 class="notion-section-title">{title}</h2>'
    if description:
        html += f'<p class="notion-section-desc">{description}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# Cards
# ============================================================

def notion_card_begin(title: str = "", subtitle: str = ""):
    """Opens a Notion-style card. Pair with notion_card_end()."""
    html = '<div class="notion-card">'
    if title:
        html += f'<h3 class="notion-card-title">{title}</h3>'
    if subtitle:
        html += f'<p class="notion-card-subtitle">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def notion_card_end():
    """Closes a Notion-style card opened by notion_card_begin()."""
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# Status Badge
# ============================================================

def notion_badge(text: str, variant: str = "info"):
    """Renders an inline status badge. Variants: 'success', 'warning', 'info'."""
    st.markdown(
        f'<span class="notion-badge notion-badge-{variant}">{text}</span>',
        unsafe_allow_html=True,
    )


# ============================================================
# Spacer
# ============================================================

def notion_spacer(px: int = 24):
    """Adds vertical whitespace."""
    st.markdown(f'<div style="height: {px}px;"></div>', unsafe_allow_html=True)


# ============================================================
# Filter Dataframe (Redesigned for Notion)
# ============================================================

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
    st.markdown('<div class="notion-filter-bar"><p class="filter-label">Filters</p>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

    return df_filtered
