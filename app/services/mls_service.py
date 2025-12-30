import requests
from typing import List, Dict


def fetch_raw_properties():
    """
    Fetch raw property data from brother's API.
    This function only fetches data.
    No cleaning, no database, no AI.
    """

    RAW_DATA_API_URL = "https://dev-sitex-1858428749.wix-development-sites.org/_functions/mlsrawdata"

    try:
        response = requests.get(RAW_DATA_API_URL, timeout=30)
        response.raise_for_status()

        data = response.json()

        # We expect data to be a list of property objects
        return data

    except requests.exceptions.RequestException as e:
        print("Error fetching raw data:", str(e))
        return []
