import requests
import os
from typing import List, Dict


def fetch_raw_properties():
    """
    Fetch raw property data from Wix MLS database.
    Uses environment variable for URL.
    """
    # Read from .env file
    RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
    
    if not RAW_DATA_API_URL:
        print("Error: RAW_DATA_API_URL not set in environment!")
        return []
    
    try:
        response = requests.get(RAW_DATA_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Error fetching raw data:", str(e))
        return []