"""
utils/id_maps.py

This module centralizes mappings from numeric IDs (likely from ESPN API)
to human-readable strings for various fantasy baseball entities such as
player positions, professional teams, statistical categories, and activity types.
"""

POSITION_MAP = {
    0: 'C',
    1: '1B',
    2: '2B',
    3: '3B',
    4: 'SS',
    5: 'OF',
    6: '2B/SS', # Combined position
    7: '1B/3B', # Combined position
    8: 'LF',
    9: 'CF',
    10: 'RF',
    11: 'DH',
    12: 'UTIL',
    13: 'P',
    14: 'SP',
    15: 'RP',
    16: 'BE', # Bench
    17: 'IL', # Injured List
    19: 'IF', # Infield
    # TODO: Confirm values for 18, 21, 22 if they exist and are needed.
}

PRO_TEAM_MAP = {
    0: 'FA',    # Free Agent
    1: 'Bal',   # Baltimore Orioles
    2: 'Bos',   # Boston Red Sox
    3: 'LAA',   # Los Angeles Angels
    4: 'ChW',   # Chicago White Sox
    5: 'Cle',   # Cleveland Guardians
    6: 'Det',   # Detroit Tigers
    7: 'KC',    # Kansas City Royals
    8: 'Mil',   # Milwaukee Brewers
    9: 'Min',   # Minnesota Twins
    10: 'NYY',  # New York Yankees
    11: 'Oak',  # Oakland Athletics
    12: 'Sea',  # Seattle Mariners
    13: 'Tex',  # Texas Rangers
    14: 'Tor',  # Toronto Blue Jays
    15: 'Atl',  # Atlanta Braves
    16: 'ChC',  # Chicago Cubs
    17: 'Cin',  # Cincinnati Reds
    18: 'Hou',  # Houston Astros
    19: 'LAD',  # Los Angeles Dodgers
    20: 'Wsh',  # Washington Nationals
    21: 'NYM',  # New York Mets
    22: 'Phi',  # Philadelphia Phillies
    23: 'Pit',  # Pittsburgh Pirates
    24: 'StL',  # St. Louis Cardinals
    25: 'SD',   # San Diego Padres
    26: 'SF',   # San Francisco Giants
    27: 'Col',  # Colorado Rockies
    28: 'Mia',  # Miami Marlins
    29: 'Ari',  # Arizona Diamondbacks
    30: 'TB',   # Tampa Bay Rays
}

STATS_MAP = {
    0: 'AB',    # At Bats
    1: 'H',     # Hits
    2: 'AVG',   # Batting Average
    3: '2B',    # Doubles
    4: '3B',    # Triples
    5: 'HR',    # Home Runs
    6: 'XBH',   # Extra Base Hits
    7: '1B',    # Singles
    8: 'TB',    # Total Bases
    9: 'SLG',   # Slugging Percentage
    10: 'B_BB',  # Batter Walks (Base on Balls)
    11: 'B_IBB', # Batter Intentional Base on Balls
    12: 'HBP',   # Hit By Pitcher
    13: 'SF',    # Sacrifice Flies
    14: 'SH',    # Sacrifice Hits
    15: 'SAC',   # Sacrifices (SF + SH)
    16: 'PA',    # Plate Appearances
    17: 'OBP',   # On-Base Percentage
    18: 'OPS',   # On-Base Plus Slugging
    19: 'RC',    # Runs Created
    20: 'R',     # Runs
    21: 'RBI',   # Runs Batted In
    23: 'SB',    # Stolen Bases
    24: 'CS',    # Caught Stealing
    25: 'SB-CS', # Stolen Bases minus Caught Stealing
    26: 'GDP',   # Grounded into Double Play
    27: 'B_SO',  # Batter Strikeouts
    28: 'PS',    # Pitches Seen
    29: 'PPA',   # Pitches Per At-Bat (or Plate Appearance?)
    31: 'CYC',   # Cycle (Hit for the Cycle)
    32: 'GP',    # Games Played (Pitcher)
    33: 'GS',    # Games Started (Pitcher)
    34: 'OUTS',  # Outs Pitched
    35: 'TBF',   # Total Batters Faced
    36: 'P',     # Pitcher (General)
    37: 'P_H',   # Pitcher Hits Allowed
    38: 'OBA',   # Opponent Batting Average
    39: 'P_BB',  # Pitcher Walks Allowed
    40: 'P_IBB', # Pitcher Intentional Walks
    41: 'WHIP',  # Walks + Hits per Innings Pitched
    42: 'HBP',   # Hit Batters (Pitcher)
    43: '00BP',  # ??? (Looks like a typo or unknown abbreviation)
    44: 'P_R',   # Pitcher Runs Allowed
    45: 'ER',    # Earned Runs
    46: 'P_HR',  # Pitcher Home Runs Allowed
    47: 'ERA',   # Earned Run Average
    48: 'K',     # Strikeouts (Pitcher)
    49: 'K/9',   # Strikeouts per 9 Innings
    50: 'WP',    # Wild Pitches
    51: 'BLK',   # Balks
    52: 'PK',    # Pickoffs
    53: 'W',     # Wins (Pitcher)
    54: 'L',     # Losses (Pitcher)
    55: 'WPCT',  # Winning Percentage (Pitcher)
    56: 'SVO',   # Save Opportunities
    57: 'SV',    # Saves
    58: 'BLSV',  # Blown Saves
    59: 'SV%',   # Save Percentage
    60: 'HLD',   # Holds
    62: 'CG',    # Complete Games
    63: 'QS',    # Quality Starts
    65: 'NH',    # No-Hitters
    66: 'PG',    # Perfect Games
    67: 'TC',    # Total Chances (Fielding)
    68: 'PO',    # Putouts
    69: 'A',     # Assists
    70: 'OFA',   # Outfield Assists
    71: 'FPCT',  # Fielding Percentage
    72: 'E',     # Errors
    73: 'DP',    # Double Plays
    74: 'B_GW',  # Batter Game Winning RBI
    75: 'B_G_L', # Batter Game Losing RBI
    76: 'P_G_W', # Pitcher Game Winning
    77: 'P_G_L', # Pitcher Game Losing
    81: 'G',     # Games
    82: 'K/BB',  # Strikeout to Walk Ratio
    83: 'SVHD',  # Saves + Holds
    99: 'STARTER'# Starter (General)
}

ACTIVITY_MAP = {
    178: 'FA ADDED',    # Free Agent Added
    180: 'WAIVER ADDED',# Waiver Added
    179: 'DROPPED',     # Dropped (different ID for same meaning)
    181: 'DROPPED',     # Dropped (different ID for same meaning)
    239: 'DROPPED',     # Dropped (different ID for same meaning)
    244: 'TRADED',      # Traded
    # Convenient reverse mappings for common activities if ever needed for lookup
    'FA': 178,
    'WAIVER': 180,
    'TRADED': 244
}