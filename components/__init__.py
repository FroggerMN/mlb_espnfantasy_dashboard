"""
components/__init__.py

Public API for the MLB Fantasy Dashboard component library.

Import components from here for the cleanest syntax::

    from components import notion_card, page_scaffold, data_table
"""

# --- Design Tokens ---
from components._tokens import (
    COLORS,
    SPACING,
    RADIUS,
    FONT_FAMILY,
    FONT_SIZES,
    PLOTLY_LAYOUT_DEFAULTS,
)

# --- Typography ---
from components.typography import (
    page_header,
    section_header,
    label_value,
    badge,
)

# --- Cards ---
from components.cards import (
    notion_card,
    stat_card,
    kv_card,
)

# --- Charts ---
from components.charts import plotly_card

# --- Empty States ---
from components.empty_states import (
    empty_state,
    no_data_card,
    missing_config_card,
)

# --- Filters ---
from components.filters import filter_dataframe

# --- Layout ---
from components.layout import (
    inject_notion_css,
    page_scaffold,
    spacer,
    divider,
)

# --- Tables ---
from components.tables import data_table

__all__ = [
    # Tokens
    "COLORS",
    "SPACING",
    "RADIUS",
    "FONT_FAMILY",
    "FONT_SIZES",
    "PLOTLY_LAYOUT_DEFAULTS",
    # Typography
    "page_header",
    "section_header",
    "label_value",
    "badge",
    # Cards
    "notion_card",
    "stat_card",
    "kv_card",
    # Charts
    "plotly_card",
    # Empty states
    "empty_state",
    "no_data_card",
    "missing_config_card",
    # Filters
    "filter_dataframe",
    # Layout
    "inject_notion_css",
    "page_scaffold",
    "spacer",
    "divider",
    # Tables
    "data_table",
]
