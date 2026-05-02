"""
utils/ui.py

Backward-compatible re-export layer.

All UI components have been moved to the ``components`` package.
This module re-exports them under the original names so that any
external or legacy code that imports from ``utils.ui`` continues to work.

**New code should import directly from** ``components`` **instead.**
"""

# Re-export everything from the component library under the old names
from components._tokens import (
    COLORS as NOTION_COLORS,
    PLOTLY_LAYOUT_DEFAULTS,
)
from components.layout import inject_notion_css, spacer as notion_spacer
from components.typography import (
    page_header as notion_page_header,
    section_header as notion_section_header,
    badge as notion_badge,
)
from components.cards import notion_card
from components.filters import filter_dataframe

# Legacy begin/end API for any code that hasn't migrated yet
import streamlit as st


def notion_card_begin(title: str = "", subtitle: str = "") -> None:
    """Opens a Notion-style card. Pair with notion_card_end().

    .. deprecated::
        Use the ``notion_card`` context manager instead::

            with notion_card("Title"):
                ...
    """
    html = '<div class="notion-card">'
    if title:
        html += f'<h3 class="notion-card-title">{title}</h3>'
    if subtitle:
        html += f'<p class="notion-card-subtitle">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def notion_card_end() -> None:
    """Closes a Notion-style card opened by notion_card_begin().

    .. deprecated::
        Use the ``notion_card`` context manager instead.
    """
    st.markdown("</div>", unsafe_allow_html=True)
