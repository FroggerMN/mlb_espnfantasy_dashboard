"""
tests/test_sitstart_scraper.py

Unit tests for data/fetch_pitcherlist_sitstart.py.
Uses unittest.mock to avoid real HTTP requests.
"""

from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from data.fetch_pitcherlist_sitstart import fetch_sit_start_data
from tests.conftest import SAMPLE_PITCHERLIST_HTML


class TestFetchSitStartData:
    def _mock_response(self, html: str, status: int = 200):
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.status_code = status
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    @patch("data.fetch_pitcherlist_sitstart.requests.get")
    def test_returns_dataframe_with_expected_columns(self, mock_get):
        mock_get.return_value = self._mock_response(SAMPLE_PITCHERLIST_HTML)
        df = fetch_sit_start_data("https://fake-url.com/sit-start")
        assert isinstance(df, pd.DataFrame)
        expected_cols = {"Player Names", "MLB Team", "Opponent", "Sit/Start Rating", "Date"}
        assert expected_cols.issubset(set(df.columns))

    @patch("data.fetch_pitcherlist_sitstart.requests.get")
    def test_extracts_correct_pitcher_count(self, mock_get):
        mock_get.return_value = self._mock_response(SAMPLE_PITCHERLIST_HTML)
        df = fetch_sit_start_data("https://fake-url.com/sit-start")
        # 2 games × 2 pitchers each = 4 rows
        assert len(df) == 4

    @patch("data.fetch_pitcherlist_sitstart.requests.get")
    def test_extracts_team_abbreviations(self, mock_get):
        mock_get.return_value = self._mock_response(SAMPLE_PITCHERLIST_HTML)
        df = fetch_sit_start_data("https://fake-url.com/sit-start")
        assert "MIN" in df["MLB Team"].values
        assert "KCR" in df["MLB Team"].values

    @patch("data.fetch_pitcherlist_sitstart.requests.get")
    def test_returns_empty_dataframe_on_request_error(self, mock_get):
        """Network/HTTP errors should return an empty DataFrame, not raise."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("No connection")
        df = fetch_sit_start_data("https://fake-url.com/sit-start")
        assert isinstance(df, pd.DataFrame)
        assert df.empty
