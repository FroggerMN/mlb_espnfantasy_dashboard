"""
components/typography.py

Notion-style typography components: page headers, section headers,
label-value pairs, and status badges.
"""

import streamlit as st


def page_header(title: str, description: str = "") -> None:
    """
    Renders a Notion-style page header with an optional description.

    Args:
        title:       The main page title (rendered as H1).
        description: Optional subtitle/description text below the title.

    Example::

        page_header(
            "MLB Fantasy Dashboard",
            "ESPN Fantasy Baseball API dashboard for your 12-team H2H league.",
        )
    """
    html = f'<div class="notion-page-header"><h1>{title}</h1>'
    if description:
        html += f'<p class="notion-page-header-desc">{description}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_header(title: str, description: str = "") -> None:
    """
    Renders a Notion-style section header (H2 + optional subtitle).

    Args:
        title:       The section title.
        description: Optional description text.

    Example::

        section_header("League Standings", "Season-to-date performance.")
    """
    html = f'<div class="notion-section"><h2 class="notion-section-title">{title}</h2>'
    if description:
        html += f'<p class="notion-section-desc">{description}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def label_value(label: str, value: str, sublabel: str = "") -> None:
    """
    Renders a small-caps label with a large value below it.
    Useful for displaying computed metrics inline (e.g. Scoring Period ID).

    Args:
        label:    The uppercase label text.
        value:    The prominent value text.
        sublabel: Optional muted text below the value.

    Example::

        label_value("Scoring Period ID", "15", "Week 2")
    """
    html = (
        f'<p style="font-size:12px; color:#6F6F6F; text-transform:uppercase; '
        f'letter-spacing:0.04em; margin-bottom:4px;">{label}</p>'
        f'<p style="font-size:22px; font-weight:600; color:#2F2F2F; margin:0;">'
        f"{value}</p>"
    )
    if sublabel:
        html += f'<p style="font-size:12px; color:#9F9F9F; margin:0;">{sublabel}</p>'
    st.markdown(html, unsafe_allow_html=True)


def badge(text: str, variant: str = "info") -> None:
    """
    Renders an inline status badge (pill).

    Args:
        text:    The badge label.
        variant: One of 'success', 'warning', 'info', 'error'.

    Example::

        badge("Loaded", "success")
        badge("Not loaded", "warning")
        badge("Failed", "error")
    """
    st.markdown(
        f'<span class="notion-badge notion-badge-{variant}">{text}</span>',
        unsafe_allow_html=True,
    )
