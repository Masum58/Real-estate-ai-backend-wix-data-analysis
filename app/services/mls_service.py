import os
import requests
from typing import Dict, List

def fetch_raw_properties() -> Dict[str, List]:
    """
    Fetch ALL 46,500 MLS properties from Vercel endpoint.
    """
    RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
    
    if not RAW_DATA_API_URL:
        print("❌ Error: RAW_DATA_API_URL not set in environment!")
        return {"items": []}
    
    try:
        print(f"🔵 Fetching all MLS data from: {RAW_DATA_API_URL}")
        print(f"⏳ Loading 46,500 properties...")
        
        # Fetch all data with extended timeout
        response = requests.get(RAW_DATA_API_URL, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            items = data.get("items", []) or data.get("properties", []) or data.get("data", [])
        elif isinstance(data, list):
            items = data
        else:
            print(f"⚠️ Unexpected data format: {type(data)}")
            items = []
        
        print(f"✅ Successfully loaded {len(items)} MLS properties")
        
        return {"items": items}
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server took longer than 120 seconds")
        return {"items": []}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return {"items": []}
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"items": []}