"""
components/empty_states.py

Standardized empty-state / no-data components.
Replaces the repeated 'no data available' HTML blocks found across every page.
"""

import streamlit as st

from components.cards import notion_card


# Default messages
_DEFAULT_NO_DATA = (
    "No roster data available. "
    'Return to the home page and click <strong>Fetch Latest Data</strong>.'
)

_DEFAULT_MISSING_CONFIG = (
    "Missing required league information. "
    "Return to the home page and configure your league settings."
)


def empty_state(
    message: str,
    icon: str = "📭",
    show_icon: bool = True,
) -> None:
    """
    Renders a standardized empty-state message inside a Notion card.

    Args:
        message:   The message to display (supports HTML).
        icon:      Emoji or character to show above the message.
        show_icon: Whether to display the icon.

    Example::

        empty_state("No data yet. Click Fetch to load.")
        empty_state("Nothing here!", icon="🔍")
    """
    with notion_card():
        if show_icon:
            st.markdown(
                f'<p style="font-size:28px; margin:0 0 8px 0;">{icon}</p>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<p style="font-size:14px; color:#6F6F6F;">{message}</p>',
            unsafe_allow_html=True,
        )


def no_data_card(message: str | None = None) -> None:
    """
    Quick shorthand for the most common "no roster data" empty state.

    Args:
        message: Override the default message. If None, uses the standard
                 roster-data-not-loaded message.

    Example::

        no_data_card()
        no_data_card("Standings not available. Click Fetch above.")
    """
    empty_state(message or _DEFAULT_NO_DATA, icon="📭", show_icon=False)


def missing_config_card(message: str | None = None) -> None:
    """
    Shorthand for pages that need session-state config to be set first.

    Args:
        message: Override the default message.

    Example::

        missing_config_card()
    """
    empty_state(message or _DEFAULT_MISSING_CONFIG, icon="⚙️", show_icon=False)
