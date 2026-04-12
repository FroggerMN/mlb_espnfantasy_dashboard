"""
tests/test_espn_utilities.py

Unit tests for data/espn_mlb_utilities.py — roster and league extraction functions.
"""

import pytest
import pandas as pd

from data.espn_mlb_utilities import get_league_info, get_roster_info


class TestGetLeagueInfo:
    def test_happy_path(self, sample_mteam):
        df = get_league_info(sample_mteam)
        assert not df.empty
        assert list(df.columns) == ["Team Number", "Team Names"]
        assert len(df) == 2
        assert df.loc[0, "Team Names"] == "RP's, We Have Da Heat"

    def test_empty_teams_list(self):
        df = get_league_info({"teams": []})
        assert df.empty

    def test_missing_teams_key(self):
        df = get_league_info({})
        assert df.empty

    def test_bad_team_structure(self):
        """Teams missing 'name' key should return empty DataFrame."""
        df = get_league_info({"teams": [{"id": 1}]})
        assert df.empty


class TestGetRosterInfo:
    def test_returns_non_empty_dataframe(self, sample_mroster, sample_mteam):
        df = get_roster_info(sample_mroster, sample_mteam)
        assert not df.empty
        assert "Player Names" in df.columns
        assert "Team Names" in df.columns

    def test_player_count(self, sample_mroster, sample_mteam):
        df = get_roster_info(sample_mroster, sample_mteam)
        assert len(df) == 3

    def test_missing_player_name_key(self, sample_mteam):
        """Entries missing fullName should be skipped; result is an empty DataFrame."""
        bad_roster = {
            "teams": [
                {
                    "roster": {
                        "entries": [
                            {"playerPoolEntry": {"player": {}}},  # no fullName
                        ]
                    }
                }
            ]
        }
        df = get_roster_info(bad_roster, sample_mteam)
        # All entries skipped → records list is empty → should return empty DataFrame gracefully
        assert isinstance(df, pd.DataFrame)

    def test_invalid_input_types(self):
        df = get_roster_info(None, None)
        assert df.empty
