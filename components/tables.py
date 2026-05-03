"""
components/tables.py

Composite data-table component that bundles filtering, card wrapping,
dataframe display, and optional CSV download into a single call.
"""

import pandas as pd
import streamlit as st

from components.cards import notion_card
from components.filters import filter_dataframe
from components.layout import spacer


def data_table(
    df: pd.DataFrame,
    key_prefix: str,
    enable_filter: bool = True,
    enable_download: bool = False,
    download_filename: str = "export.csv",
    download_label: str = "Download CSV",
    height: int | None = None,
    hide_index: bool = True,
    enable_selection: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, list[int]]:
    """
    All-in-one data table: filter bar → card-wrapped ``st.dataframe`` →
    optional CSV download button.

    Replaces the 4–5 line pattern repeated in Athletic Rankings,
    PitchersList Rankings, and other ranking tab views.

    Args:
        df:                The source DataFrame.
        key_prefix:        Unique key prefix for filter widgets.
        enable_filter:     Whether to show the filter UI (default True).
        enable_download:   Whether to show a CSV download button (default False).
        download_filename: Filename for the CSV download.
        download_label:    Label text for the download button.
        height:            Optional fixed height for the dataframe widget.
        hide_index:        Whether to hide the DataFrame index (default True).

    Returns:
        The (possibly filtered) DataFrame that was displayed.

    Example::

        data_table(rankings_df, key_prefix="sp100", enable_download=True)
    """
    # Filter
    if enable_filter:
        filtered_df = filter_dataframe(df, key_prefix)
    else:
        filtered_df = df

    # Card-wrapped dataframe
    with notion_card():
        kwargs = {"use_container_width": True, "hide_index": hide_index}
        if height is not None:
            kwargs["height"] = height
            
        if enable_selection:
            kwargs["on_select"] = "rerun"
            kwargs["selection_mode"] = "multi-row"
            
        selection = st.dataframe(filtered_df, **kwargs)

        # Download button
        if enable_download:
            spacer(8)
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=download_label,
                data=csv_data,
                file_name=download_filename,
                mime="text/csv",
            )

    if enable_selection:
        return filtered_df, selection.selection.rows
    return filtered_df
