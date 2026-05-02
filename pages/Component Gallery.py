"""
Component Gallery — Interactive demo of all reusable UI components.

This page lives in ``pages/`` so it appears in the Streamlit sidebar.
It showcases every component in the library with live examples.
"""

import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from components.layout import page_scaffold, spacer, divider, inject_notion_css
from components.typography import page_header, section_header, label_value, badge
from components.cards import notion_card, stat_card, kv_card
from components.charts import plotly_card
from components.empty_states import empty_state, no_data_card, missing_config_card
from components.filters import filter_dataframe
from components.tables import data_table
from components._tokens import COLORS, SPACING, RADIUS, FONT_SIZES


def _sample_df() -> pd.DataFrame:
    """Returns a small sample DataFrame for demos."""
    return pd.DataFrame({
        "Player Names": ["Aaron Judge", "Shohei Ohtani", "Mookie Betts", "Freddie Freeman", "Trea Turner"],
        "Team Names": ["RP's, We Have Da Heat", "Available", "RP's, We Have Da Heat", "Available", "Available"],
        "HR": [62, 44, 35, 21, 21],
        "AVG": [.311, .304, .307, .331, .298],
        "Position": ["OF", "DH", "OF", "1B", "SS"],
    })


def main():
    """Renders the component gallery."""
    page_scaffold(
        "Component Gallery",
        "Interactive showcase of every reusable UI component in the library.",
        page_title="Component Gallery",
        icon="🧩",
    )

    spacer(16)

    # ── TYPOGRAPHY ──────────────────────────────────────────────
    section_header("Typography", "Headers, labels, and badges.")

    with notion_card():
        st.code('from components.typography import page_header, section_header, label_value, badge', language="python")

    spacer(8)

    col1, col2 = st.columns(2)
    with col1:
        with notion_card("page_header()"):
            st.markdown(
                '<div class="notion-page-header"><h1>Page Title</h1>'
                '<p class="notion-page-header-desc">Optional description text.</p></div>',
                unsafe_allow_html=True,
            )
    with col2:
        with notion_card("section_header()"):
            section_header("Section Title", "Optional description.")

    spacer(8)

    col3, col4 = st.columns(2)
    with col3:
        with notion_card("label_value()"):
            label_value("Scoring Period ID", "15", "Week 2")
    with col4:
        with notion_card("badge()"):
            badge("Loaded", "success")
            spacer(4)
            badge("Pending", "warning")
            spacer(4)
            badge("Active", "info")
            spacer(4)
            badge("Failed", "error")

    divider()

    # ── CARDS ────────────────────────────────────────────────────
    section_header("Cards", "Card wrappers, stat cards, and key-value cards.")

    with notion_card():
        st.code(
            'from components.cards import notion_card, stat_card, kv_card\n\n'
            'with notion_card("Title", "Subtitle"):\n'
            '    st.write("Card content here")',
            language="python",
        )

    spacer(8)

    col5, col6, col7 = st.columns(3)
    with col5:
        with notion_card("Basic Card", "With title and subtitle"):
            st.write("Any Streamlit content goes inside.")
    with col6:
        stat_card("Home Runs", "62", "Aaron Judge · 2022")
    with col7:
        kv_card("Config", {"League ID": "64175", "Year": "2026", "Week": "2"})

    divider()

    # ── TABLES ───────────────────────────────────────────────────
    section_header("Tables", "All-in-one data table with filter and download.")

    with notion_card():
        st.code(
            'from components.tables import data_table\n\n'
            'data_table(df, key_prefix="demo", enable_download=True)',
            language="python",
        )

    spacer(8)

    sample_df = _sample_df()
    data_table(
        sample_df,
        key_prefix="gallery_demo",
        enable_download=True,
        download_filename="gallery_sample.csv",
        download_label="Download Sample CSV",
    )

    divider()

    # ── CHARTS ───────────────────────────────────────────────────
    section_header("Charts", "Plotly figures wrapped in styled cards with design tokens applied.")

    with notion_card():
        st.code(
            'from components.charts import plotly_card\n\n'
            'fig = go.Figure()\n'
            'fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6]))\n'
            'plotly_card(fig, key="demo_chart")',
            language="python",
        )

    spacer(8)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, 11)),
        y=[12, 15, 13, 17, 14, 19, 16, 22, 18, 24],
        mode="lines+markers",
        name="Series A",
        line=dict(width=2, color=COLORS["accent"]),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=list(range(1, 11)),
        y=[10, 11, 14, 13, 16, 15, 18, 17, 20, 21],
        mode="lines+markers",
        name="Series B",
        line=dict(width=2, color="#D97706"),
        marker=dict(size=6),
    ))
    fig.update_layout(
        title=dict(text="Sample Chart — 10-Week Trend", font=dict(size=15)),
    )
    plotly_card(fig, key="gallery_chart")

    divider()

    # ── EMPTY STATES ─────────────────────────────────────────────
    section_header("Empty States", "Standardized messages for missing data.")

    with notion_card():
        st.code(
            'from components.empty_states import empty_state, no_data_card, missing_config_card\n\n'
            'no_data_card()\n'
            'missing_config_card()\n'
            'empty_state("Custom message here.", icon="🔍")',
            language="python",
        )

    spacer(8)

    col8, col9, col10 = st.columns(3)
    with col8:
        st.caption("no_data_card()")
        no_data_card()
    with col9:
        st.caption("missing_config_card()")
        missing_config_card()
    with col10:
        st.caption("empty_state() with icon")
        empty_state("Nothing to show yet — try searching.", icon="🔍")

    divider()

    # ── LAYOUT ───────────────────────────────────────────────────
    section_header("Layout", "Page scaffold, spacers, and dividers.")

    with notion_card():
        st.code(
            'from components.layout import page_scaffold, spacer, divider\n\n'
            '# One-call page bootstrap (replaces 3-line boilerplate)\n'
            'page_scaffold("Page Title", "Description", page_title="Tab Title")\n\n'
            'spacer(16)  # 16px vertical whitespace\n'
            'divider()   # Styled horizontal rule',
            language="python",
        )

    divider()

    # ── DESIGN TOKENS ────────────────────────────────────────────
    section_header("Design Tokens", "Centralized constants for colors, spacing, and typography.")

    with notion_card():
        st.code(
            'from components._tokens import COLORS, SPACING, RADIUS, FONT_SIZES\n\n'
            f'COLORS = {{\n'
            f'    "bg_primary": "{COLORS["bg_primary"]}",\n'
            f'    "accent": "{COLORS["accent"]}",\n'
            f'    "text_primary": "{COLORS["text_primary"]}",\n'
            f'    ...  # {len(COLORS)} total tokens\n'
            f'}}\n\n'
            f'SPACING = {SPACING}\n'
            f'RADIUS  = {RADIUS}\n'
            f'FONT_SIZES = {FONT_SIZES}',
            language="python",
        )

    spacer(8)

    # Color swatches
    with notion_card("Color Palette"):
        swatch_html = '<div style="display:flex; flex-wrap:wrap; gap:8px;">'
        for name, hex_val in COLORS.items():
            if hex_val.startswith("rgba"):
                continue  # Skip rgba values for swatches
            text_color = "#FFFFFF" if name.startswith(("text", "accent")) and "light" not in name else "#2F2F2F"
            swatch_html += (
                f'<div style="background:{hex_val}; color:{text_color}; '
                f'padding:8px 12px; border-radius:6px; font-size:11px; '
                f'font-family:monospace; border:1px solid #E5E5E0; min-width:120px;">'
                f'{name}<br/>{hex_val}</div>'
            )
        swatch_html += '</div>'
        st.markdown(swatch_html, unsafe_allow_html=True)

    spacer(24)


if __name__ == "__main__":
    main()
