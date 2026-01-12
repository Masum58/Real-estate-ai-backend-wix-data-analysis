import requests
from typing import Optional, Dict

def geocode_from_mlsgrid(address: str, city: str, state: str, zip_code: str) -> Optional[Dict]:
    """
    Use MLSGrid API to get coordinates for a specific address.
    Only 1 API call per valuation - safe for rate limits.
    
    Args:
        address: Street address (e.g., "510 Martha Ave")
        city: City name (e.g., "Charlotte")
        state: State code (e.g., "NC")
        zip_code: ZIP code (e.g., "28202")
    
    Returns:
        {"latitude": float, "longitude": float} or None
    """
    
    BASE_URL = "https://api.mlsgrid.com/v2/Property"
    ACCESS_TOKEN = "97f05f8b677637436e09f6d4d20f455f3eb8b965"
    
    try:
        # Try exact address match first
        filter_string = f"UnparsedAddress eq '{address}' and City eq '{city}'"
        
        params = {
            "$filter": filter_string,
            "$select": "Latitude,Longitude,UnparsedAddress",
            "$top": 1
        }
        
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        
        print(f"🔵 MLSGrid: Searching for '{address}, {city}, {state}'...")
        
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get("value", [])
            
            if properties and properties[0].get("Latitude") and properties[0].get("Longitude"):
                coords = {
                    "latitude": properties[0]["Latitude"],
                    "longitude": properties[0]["Longitude"]
                }
                print(f"✅ MLSGrid found: {coords['latitude']}, {coords['longitude']}")
                return coords
            else:
                print(f"⚠️ MLSGrid: Address found but no coordinates")
        
        # If exact match fails, try broader search (just city + zip)
        print(f"⚠️ Trying broader search in {city} {zip_code}...")
        
        filter_string = f"City eq '{city}' and PostalCode eq '{zip_code}'"
        params["$filter"] = filter_string
        params["$top"] = 5
        
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get("value", [])
            
            if properties:
                # Use first property's coordinates as approximate center
                coords = {
                    "latitude": properties[0].get("Latitude"),
                    "longitude": properties[0].get("Longitude")
                }
                print(f"✅ MLSGrid: Using approximate center of {city} {zip_code}")
                print(f"   Coordinates: {coords['latitude']}, {coords['longitude']}")
                return coords
        
        print(f"⚠️ MLSGrid: No results for {city}, {state}")
        return None
        
    except requests.exceptions.Timeout:
        print("⚠️ MLSGrid API timeout")
        return None
        
    except Exception as e:
        print(f"⚠️ MLSGrid error: {str(e)}")
        return None
