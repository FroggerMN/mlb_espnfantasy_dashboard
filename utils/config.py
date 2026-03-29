# config.

# --- Global Application Constants ---

# List of ESPN data views to fetch for the main dashboard
VIEWLIST = ('mTeam', 'mRoster', 'mBoxscore')

# Default ESPN League Settings
DEFAULT_YEAR = 2026
DEFAULT_SCORING_PERIOD_WEEK = 14
DEFAULT_LEAGUE_ID = 64175
DEFAULT_ESPN_S2 ='AEAxz37BvE%2B1ljLaXEBgDEU2ecOl9nvEC9VSgBVJFfH8jH3dYjSjvbu5h61LBOSwjmlNp5QjcMP2NkhQ0%2Btum%2Fqf6FOn2yzkzWXqYqlYjC9uOaZ8HWnN4WFOLlzTFVv8N%2BgFFW4yhQlHkjdYOwQaer6bPxJ5qAZZgDhBw1oYJOGSpCQtZsXPBNf5hx95%2Fe83r%2BdIk%2BboVPllCMjbhopZOqK8B2nrwGpjJveJ%2BPL5tq0d0RNdErAJqhK7sK5iu6hkC9j%2Bz9udlVMm%2FcYQWMsAXVBz'
DEFAULT_SWID ='{3F15FCEB-EB45-4EE7-B1B1-92B76369484D}'
# File path for storing PitcherList URLs (used by pages/PitcherList_Rankings.py)
URLS_FILE = "data/pitcherlist_urls.json"

# Default PitcherList URLs (initial values, can be updated via UI)
# These are the *default* initial URLs.
# The application logic handles saving/loading them from URLS_FILE.
DEFAULT_RANKINGS_URLS = {
    'sp_100_df': 'https://pitcherlist.com/top-100-starting-pitchers-for-2025-fantasy-baseball-week-8-5-19/',
    'sh_100_df': 'https://pitcherlist.com/rp-ranks-5-23-the-top-100-relievers-for-savehold-leagues//',
    'hitters_150_df': 'https://pitcherlist.com/top-150-hitters-for-fantasy-baseball-2025-week-8-5-22/',
}

# Supported fantasy stat categories for the 10-category league
# (Centralized here as they are core to the league's definition)
TARGET_STATS = ['R', 'HR', 'RBI', 'SB', 'AVG', 'K', 'W', 'ERA', 'WHIP', 'SVHD']

STAT_COMPONENTS = {
    'AVG': ['H', 'AB'],
    'ERA': ['ER', 'OUTS'],
    'WHIP': ['P_BB', 'P_H', 'OUTS']
}

# Statistical categories where a lower value indicates better performance
# (Used in Roto calculations)
STATS_LOW_IS_BETTER = {'ERA', 'WHIP'}


# Configuration handling
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default."""
    return os.environ.get(key, default)

# Allow overrides via environment variables
DEFAULT_LEAGUE_ID = int(get_env_or_default('ESPN_LEAGUE_ID', '64175'))
DEFAULT_ESPN_S2 = get_env_or_default('ESPN_S2', DEFAULT_ESPN_S2)
DEFAULT_SWID = get_env_or_default('ESPN_SWID', DEFAULT_SWID)

def validate_config() -> bool:
    """Validate configuration values."""
    if not DEFAULT_ESPN_S2 or not DEFAULT_SWID:
        logger.warning("ESPN credentials not configured - private leagues may not work")
        return False
    return True