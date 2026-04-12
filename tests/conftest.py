"""
tests/conftest.py

Shared pytest fixtures for the MLB Fantasy Dashboard test suite.
"""

import pytest
import pandas as pd


# ---------------------------------------------------------------------------
# ESPN raw API fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_mteam():
    """Minimal mTeam API response with two teams."""
    return {
        "teams": [
            {"id": 1, "name": "RP's, We Have Da Heat"},
            {"id": 2, "name": "The Other Team"},
        ]
    }


@pytest.fixture
def sample_mroster(sample_mteam):
    """Minimal mRoster API response matching sample_mteam."""
    return {
        "teams": [
            {
                "roster": {
                    "entries": [
                        {"playerPoolEntry": {"player": {"fullName": "Justin Verlander"}}},
                        {"playerPoolEntry": {"player": {"fullName": "Max Scherzer"}}},
                    ]
                }
            },
            {
                "roster": {
                    "entries": [
                        {"playerPoolEntry": {"player": {"fullName": "Gerrit Cole"}}},
                    ]
                }
            },
        ]
    }


@pytest.fixture
def sample_roster_df():
    """Pre-built cleaned roster DataFrame for merge tests."""
    return pd.DataFrame(
        {
            "Team Number": [1, 1, 2],
            "Player Names": ["justin verlander", "max scherzer", "gerrit cole"],
            "Team Names": ["RP's, We Have Da Heat", "RP's, We Have Da Heat", "The Other Team"],
        }
    )


# ---------------------------------------------------------------------------
# PitcherList HTML fixture
# ---------------------------------------------------------------------------

SAMPLE_PITCHERLIST_HTML = """
<html><body>
<table>
  <tr><td colspan="6">Monday – 3/30</td></tr>
  <tr><td>Date</td><td>Game</td><td>Away Pitcher</td><td>Sit / Start</td><td>Home Pitcher</td><td>Sit / Start</td></tr>
  <tr><td>3/30</td><td>MIN at KCR</td><td>M. Abel</td><td>Maybe-5</td><td>K. Bubic</td><td>Start-7</td></tr>
  <tr><td>3/30</td><td>TEX at BAL</td><td>J. Leiter</td><td>Maybe-4</td><td>C. Bassitt</td><td>Sit-3</td></tr>
</table>
</body></html>
"""
