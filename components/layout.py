"""
components/layout.py

Layout utilities: page scaffolding, spacers, and dividers.
"""

from pathlib import Path

import streamlit as st


def inject_notion_css() -> None:
    """
    Loads and injects the Notion design-system CSS into the Streamlit page.

    Reads ``assets/styles.css`` relative to the project root and injects it
    via ``st.markdown``.  Called once per page, typically inside
    :func:`page_scaffold`.

    Example::

        inject_notion_css()
    """
    import logging

    logger = logging.getLogger(__name__)
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    try:
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        logger.warning("Could not find assets/styles.css — Notion CSS not loaded.")


def page_scaffold(
    title: str,
    description: str = "",
    page_title: str = "",
    icon: str = "⚾",
) -> None:
    """
    One-call page bootstrap that replaces the 3-line boilerplate repeated
    on every page:

    1. ``st.set_page_config(...)``
    2. ``inject_notion_css()``
    3. ``page_header(...)``

    Args:
        title:      The visible page title (rendered as H1).
        description: Optional subtitle text.
        page_title: The browser tab title.  Defaults to *title* if empty.
        icon:       Page icon shown in the browser tab (default ⚾).

    Example::

        page_scaffold(
            "Athletic Rankings",
            "Player rankings sourced from The Athletic.",
        )
    """
    from components.typography import page_header

    st.set_page_config(
        page_title=page_title or title,
        layout="wide",
        page_icon=icon,
    )
    inject_notion_css()
    page_header(title, description)


def spacer(px: int = 24) -> None:
    """
    Adds vertical whitespace.

    Args:
        px: Height in pixels (default 24).  Use values from the spacing
            scale: 4, 8, 12, 16, 24, 32.

    Example::

        spacer(8)
        spacer(32)
    """
    st.markdown(f'<div style="height: {px}px;"></div>', unsafe_allow_html=True)


def divider() -> None:
    """
    Renders a styled horizontal rule using the design-system border color.

    Example::

        divider()
    """
    st.markdown(
        '<hr style="border:none; border-top:1px solid #E5E5E0; margin:24px 0;" />',
        unsafe_allow_html=True,
    )
