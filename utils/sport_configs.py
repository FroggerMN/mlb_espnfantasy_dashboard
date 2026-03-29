# utils/sport_configs.py
"""
Sport-specific configurations and mappings.
"""
from data.data_types import SportConfig, SportType

# Baseball configuration
BASEBALL_CONFIG = SportConfig(
    name="Baseball",
    default_views=['mTeam', 'mRoster', 'mBoxscore'],
    stat_categories=['R', 'HR', 'RBI', 'SB', 'AVG', 'K', 'W', 'ERA', 'WHIP', 'SVHD'],
    stat_components={
        'AVG': ['H', 'AB'],
        'ERA': ['ER', 'OUTS'],
        'WHIP': ['P_BB', 'P_H', 'OUTS']
    },
    stats_low_is_better={'ERA', 'WHIP'},
    position_map={
        0: 'C', 1: '1B', 2: '2B', 3: '3B', 4: 'SS', 5: 'OF',
        13: 'P', 14: 'SP', 15: 'RP', 16: 'BE', 17: 'IL'
    }
)

# Football configuration (example)
FOOTBALL_CONFIG = SportConfig(
    name="Football", 
    default_views=['mTeam', 'mRoster', 'mMatchup'],
    stat_categories=['PASS_YDS', 'PASS_TDS', 'RUSH_YDS', 'RUSH_TDS', 'REC_YDS', 'REC_TDS'],
    stat_components={},
    stats_low_is_better={'INT', 'FUM'},
    position_map={
        0: 'QB', 1: 'TQB', 2: 'RB', 3: 'RB/WR', 4: 'WR', 5: 'WR/TE',
        6: 'TE', 7: 'OP', 8: 'DT', 9: 'DE', 10: 'LB', 11: 'DL',
        12: 'CB', 13: 'S', 14: 'DB', 15: 'DP', 16: 'D/ST', 17: 'K', 20: 'BE', 21: 'IR'
    }
)

# Sport configurations dictionary
SPORT_CONFIGS = {
    SportType.BASEBALL: BASEBALL_CONFIG,
    SportType.FOOTBALL: FOOTBALL_CONFIG,
}