# utils/decorators.py
import pandas as pd
from functools import wraps
import streamlit as st

def streamlit_cache(func):
    """Custom cache decorator for Streamlit functions."""
    @wraps(func)
    @st.cache_data(ttl=3600)  # 1 hour TTL
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# Usage
@streamlit_cache
def load_and_process_data(league_id: int, week: int) -> pd.DataFrame:
    # Your data processing logic
    pass