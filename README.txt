# MLB Fantasy Dashboard

This project is a Streamlit application designed for managing an ESPN fantasy baseball team (12-team, H2H).
It fetches ESPN API data and visualizes your league's statistics, category rolling averages, and integrated player rankings.

## How to Run the App

1. Open your terminal (Command Prompt, PowerShell, etc.).
2. Navigate to the project root directory where `app.py` is located. For example:
   ```
   cd C:\Users\frogg\Documents\python_scripts\fanatsy_sports\espn_fantasy\espn_flb_inseason\mlb_fantasy_dashboard_V2
   ```
3. Ensure you have installed all the required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Start the Streamlit application by running:
   ```
   python -m streamlit run app.py


   ```
5. A new browser window/tab will automatically open (usually at `http://localhost:8501`).
6. In the left sidebar of the application, input your target ESPN League ID, Season Year, and Authentication Cookies (ESPN_S2 / SWID).
7. Click the **Fetch Latest Data** button to sync the application with your current ESPN league rosters.
