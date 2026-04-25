# MLB Fantasy Dashboard

A Streamlit-based dashboard for managing a 12-team, Head-to-Head ESPN Fantasy Baseball league. It fetches live data from the ESPN API, processes weekly category stats, and integrates 3rd-party rankings from PitcherList and The Athletic.

---

## Directory Layout

```
mlb_fantasy_dashboard_V2/
├── app.py                          # Entry point — sidebar, session state, ESPN fetch
├── pages/
│   ├── Athletic Rankings.py        # The Athletic CSV rankings merged with rosters
│   ├── Category Rolling Average.py # Plotly rolling-average charts per stat category
│   └── PitchersList Rankings.py   # SP100 / RP100 / Hitters150 / Start-Sit tabs
├── data/
│   ├── espn_mlb_utilities.py       # ESPN API data extraction & stat calculations
│   ├── fetch_espn_data.py          # Raw HTTP requests to ESPN API + JSON caching
│   ├── fetch_pitcherlist_ranking.py# pd.read_html scraper for PitcherList rankings
│   ├── fetch_pitcherlist_sitstart.py# Weekly Start/Sit matchup scraper
│   ├── espn_json/                  # Cached ESPN API JSON responses
│   └── googlesheets/               # Athletic Rankings CSVs (downloaded manually)
├── utils/
│   ├── config.py                   # Constants, stat category definitions
│   ├── id_maps.py                  # ESPN stat ID → name mapping
│   ├── logging_config.py           # Central logging setup (call once at startup)
│   ├── rankings_utilities.py       # Player name cleaning & formatting helpers
│   ├── sport_configs.py            # Sport-specific ESPN configurations
│   └── ui.py                       # Shared Streamlit UI components (filter_dataframe)
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_espn_utilities.py      # Tests for roster/league extraction
│   ├── test_rankings_utilities.py  # Tests for name cleaning utilities
│   └── test_sitstart_scraper.py    # Tests for Start/Sit HTTP scraper (mocked)
├── logs/                           # Auto-created — rotating log files (gitignored)
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## Dev Setup

```powershell
# 1. Clone / navigate to the project
cd mlb_fantasy_dashboard_V2

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install all dependencies
pip install -r requirements.txt
```

---

## Running the App Locally

```powershell
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

Fill in the sidebar:
- **League ID**, **Year**, **Scoring Period ID**
- **ESPN_S2** and **SWID** cookies (from your browser's ESPN session)
- Click **Fetch Latest Data**

---

## Running Tests

```powershell
# Run all tests quietly
pytest tests/ -q

# Run with coverage report
pytest tests/ -q --cov=data --cov=utils --cov-report=term-missing
```

---

## Logging

Logs are written to `logs/dashboard.log` (rotating, max 2 MB, 3 backups).  
WARNING+ messages also appear in the terminal.  
The `logs/` directory is created automatically on first run.

---

## Docker (Production)

```powershell
# Build
docker build -t mlb-fantasy-dashboard .

# Run (pass credentials as environment variables, not baked into the image)
docker run -p 8501:8501 `
  -e ESPN_LEAGUE_ID=64175 `
  -e ESPN_S2="your-cookie" `
  -e ESPN_SWID="{your-swid}" `
  mlb-fantasy-dashboard
```
