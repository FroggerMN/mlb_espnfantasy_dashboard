"""
components/charts.py

Plotly chart wrapper that applies Notion design tokens and
renders the figure inside a styled card.
"""

import streamlit as st

from components._tokens import PLOTLY_LAYOUT_DEFAULTS, COLORS


def plotly_card(fig, key: str = "", height: int = 380) -> None:
    """
    Wraps a Plotly figure in a Notion card and applies the design-system
    layout defaults automatically.

    The caller builds the ``fig`` with their own traces; this function
    merges in typography, background, grid, and margin settings from
    the design tokens before rendering.

    Args:
        fig:    A ``plotly.graph_objs.Figure`` instance.
        key:    Optional unique key for the Streamlit chart widget.
        height: Chart height in pixels (default 380).

    Example::

        import plotly.graph_objs as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], name="Series A"))
        plotly_card(fig, key="my_chart")
    """
    fig.update_layout(height=height, **PLOTLY_LAYOUT_DEFAULTS)

    st.markdown('<div class="notion-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, width='stretch', key=key or None)
    st.markdown("</div>", unsafe_allow_html=True)
