"""
components/cards.py

Notion-style card components: context-manager card wrapper,
stat display card, and key-value list card.
"""

from contextlib import contextmanager
from typing import Dict

import streamlit as st


@contextmanager
def notion_card(title: str = "", subtitle: str = ""):
    """
    Context manager that wraps its body in a Notion-style card.

    Replaces the old ``notion_card_begin()`` / ``notion_card_end()`` pair
    with a clean ``with`` block.

    Args:
        title:    Optional H3 title inside the card.
        subtitle: Optional subtitle below the title.

    Example::

        with notion_card("Roster Data"):
            st.dataframe(df)
    """
    html = '<div class="notion-card">'
    if title:
        html += f'<h3 class="notion-card-title">{title}</h3>'
    if subtitle:
        html += f'<p class="notion-card-subtitle">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


def stat_card(label: str, value: str, sublabel: str = "") -> None:
    """
    Renders a styled metric-like card with a label, large value, and optional sublabel.

    Wraps the content in a Notion card automatically.

    Args:
        label:    The uppercase metric label (e.g. "Scoring Period ID").
        value:    The prominent value (e.g. "15").
        sublabel: Optional context text below the value (e.g. "Week 2").

    Example::

        stat_card("Scoring Period ID", "15", "Week 2")
    """
    from components.typography import label_value

    with notion_card():
        label_value(label, value, sublabel)


def kv_card(title: str, items: Dict[str, str]) -> None:
    """
    Renders a card with a title and a list of key-value pairs.

    Useful for settings display, URL lists, metadata, etc.

    Args:
        title: The card title.
        items: Dictionary of label → value pairs to display.

    Example::

        kv_card("Current URLs", {
            "Top 100 SP": "https://pitcherlist.com/...",
            "Top 100 RP": "https://pitcherlist.com/...",
        })
    """
    with notion_card(title):
        for label, value in items.items():
            st.markdown(
                f'<p style="margin:4px 0;">'
                f'<span style="font-size:12px; color:#6F6F6F; '
                f'text-transform:uppercase; letter-spacing:0.04em;">{label}</span><br/>'
                f'<span style="font-size:13px; color:#2F2F2F; word-break:break-all;">'
                f"{value}</span></p>",
                unsafe_allow_html=True,
            )
