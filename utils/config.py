# config.

# --- Global Application Constants ---

# List of ESPN data views to fetch for the main dashboard
VIEWLIST = ('mTeam', 'mRoster', 'mBoxscore')

# Default ESPN League Settings
DEFAULT_YEAR = 2026
DEFAULT_SCORING_PERIOD_WEEK = 14
DEFAULT_LEAGUE_ID = 64175
# File path for storing PitcherList URLs (used by pages/PitcherList_Rankings.py)
URLS_FILE = "data/pitcherslist_urls.json"

# Default PitcherList URLs (initial values, can be updated via UI)
# These are the *default* initial URLs.
# The application logic handles saving/loading them from URLS_FILE.
def _load_default_urls():
    import os, json
    if os.path.exists(URLS_FILE):
        try:
            with open(URLS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'sp_100_df': 'https://pitcherlist.com/top-100-starting-pitchers-for-2025-fantasy-baseball-week-8-5-19/',
        'sh_100_df': 'https://pitcherlist.com/rp-ranks-5-23-the-top-100-relievers-for-savehold-leagues//',
        'hitters_150_df': 'https://pitcherlist.com/top-150-hitters-for-fantasy-baseball-2025-week-8-5-22/',
    }

DEFAULT_RANKINGS_URLS = _load_default_urls()

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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default."""
    return os.environ.get(key, default)

# Allow overrides via environment variables
DEFAULT_LEAGUE_ID = int(get_env_or_default('ESPN_LEAGUE_ID', '64175'))
DEFAULT_ESPN_S2 = get_env_or_default('ESPN_S2', '')
DEFAULT_SWID = get_env_or_default('ESPN_SWID', '')

def validate_config() -> bool:
    """Validate configuration values."""
    if not DEFAULT_ESPN_S2 or not DEFAULT_SWID:
        logger.warning("ESPN credentials not configured - private leagues may not work")
        return False
    return True