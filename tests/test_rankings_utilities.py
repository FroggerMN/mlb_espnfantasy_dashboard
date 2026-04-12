"""
tests/test_rankings_utilities.py

Unit tests for utils/rankings_utilities.py — name cleaning and formatting helpers.
"""

import pytest
import pandas as pd

from utils.rankings_utilities import clean_players_names, full_name_2_initial_last


class TestCleanPlayersNames:
    def _make_df(self, names):
        return pd.DataFrame({"Player Names": names})

    def test_accented_characters(self):
        df = self._make_df(["Félix Hernández"])
        result = clean_players_names(df, "Player Names")
        assert result["Player Names"].iloc[0] == "felix hernandez"

    def test_jr_suffix_stripped(self):
        df = self._make_df(["Ronald Acuña Jr."])
        result = clean_players_names(df, "Player Names")
        assert " jr." not in result["Player Names"].iloc[0]

    def test_lowercase_output(self):
        df = self._make_df(["GERRIT COLE"])
        result = clean_players_names(df, "Player Names")
        assert result["Player Names"].iloc[0] == result["Player Names"].iloc[0].lower()

    def test_missing_column_raises(self):
        df = pd.DataFrame({"Other Column": ["value"]})
        with pytest.raises(ValueError, match="Column 'Player Names' not found"):
            clean_players_names(df, "Player Names")

    def test_preserves_other_columns(self):
        df = pd.DataFrame({"Player Names": ["Max Scherzer"], "Rank": [1]})
        result = clean_players_names(df, "Player Names")
        assert "Rank" in result.columns
        assert result["Rank"].iloc[0] == 1


class TestFullName2InitialLast:
    def test_simple_name(self):
        assert full_name_2_initial_last("Justin Verlander") == "J. Verlander"

    def test_single_word(self):
        result = full_name_2_initial_last("Verlander")
        # Single part — last is same as first
        assert result == "V. Verlander"

    def test_empty_string(self):
        assert full_name_2_initial_last("") == ""

    def test_non_string_input(self):
        assert full_name_2_initial_last(None) == ""  # type: ignore[arg-type]
        assert full_name_2_initial_last(123) == ""  # type: ignore[arg-type]

    def test_three_part_name(self):
        result = full_name_2_initial_last("Luis Garcia Jr")
        # Should give first initial + last part
        assert result == "L. Jr"
