import os
import requests
import time
from typing import Dict, List

# Global cache with 1-hour TTL
_mls_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 3600  # 1 hour
}

def fetch_raw_properties() -> Dict[str, List]:
    """
    Fetch MLS properties with caching and memory optimization.
    Filters out invalid/extreme properties to reduce memory usage.
    """
    global _mls_cache
    
    RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
    
    if not RAW_DATA_API_URL:
        print("❌ Error: RAW_DATA_API_URL not set in environment!")
        return {"items": []}
    
    # Check cache first
    current_time = time.time()
    
    if _mls_cache["data"] is not None and _mls_cache["timestamp"] is not None:
        time_since_cache = current_time - _mls_cache["timestamp"]
        if time_since_cache < _mls_cache["ttl"]:
            print(f"✅ Using cached MLS data ({len(_mls_cache['data'])} properties)")
            print(f"   Cache age: {int(time_since_cache/60)} minutes")
            return {"items": _mls_cache["data"]}
        else:
            print(f"⏰ Cache expired ({int(time_since_cache/60)} minutes old), refreshing...")
    
    try:
        print(f"🔵 Fetching MLS data from: {RAW_DATA_API_URL}")
        print(f"⏳ Loading properties...")
        
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
        
        print(f"✅ Loaded {len(items)} properties from API")
        
        # MEMORY OPTIMIZATION: Filter immediately to reduce RAM usage
        print(f"🔧 Filtering for quality and memory optimization...")
        
        filtered = []
        skipped = {
            "missing_fields": 0,
            "extreme_price": 0,
            "extreme_size": 0,
            "invalid_data": 0
        }
        
        for prop in items:
            try:
                # Skip if missing critical fields
                if not all([
                    prop.get('city'),
                    prop.get('price'),
                    prop.get('areaSqft'),
                    prop.get('bedrooms'),
                    prop.get('bathrooms'),
                    prop.get('yearBuilt')
                ]):
                    skipped["missing_fields"] += 1
                    continue
                
                # Get values for validation
                price = prop.get('price', 0)
                sqft = prop.get('areaSqft', 0)
                bedrooms = prop.get('bedrooms', 0)
                bathrooms = prop.get('bathrooms', 0)
                
                # Skip extreme/invalid prices (likely errors or commercial)
                if price < 10000 or price > 2000000:
                    skipped["extreme_price"] += 1
                    continue
                
                # Skip extreme sizes (likely errors or commercial)
                if sqft < 300 or sqft > 10000:
                    skipped["extreme_size"] += 1
                    continue
                
                # Skip invalid bedroom/bathroom counts
                if bedrooms < 1 or bedrooms > 10 or bathrooms < 0.5 or bathrooms > 10:
                    skipped["invalid_data"] += 1
                    continue
                
                # Property passed all filters - keep it
                filtered.append(prop)
                
            except Exception as e:
                skipped["invalid_data"] += 1
                continue
        
        # Log filtering results
        total_skipped = sum(skipped.values())
        print(f"✅ Filtered to {len(filtered)} valid properties")
        print(f"   Skipped {total_skipped} properties:")
        for reason, count in skipped.items():
            if count > 0:
                print(f"     - {reason}: {count}")
        
        memory_saved = ((len(items) - len(filtered)) / len(items) * 100) if items else 0
        print(f"   Memory saved: ~{memory_saved:.1f}%")
        
        # Update cache
        _mls_cache["data"] = filtered
        _mls_cache["timestamp"] = current_time
        
        print(f"✅ Cached {len(filtered)} properties (TTL: 1 hour)")
        
        return {"items": filtered}
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server took longer than 120 seconds")
        
        # Return cached data if available (even if expired)
        if _mls_cache["data"] is not None:
            print(f"⚠️ Using stale cache ({len(_mls_cache['data'])} properties)")
            return {"items": _mls_cache["data"]}
        
        return {"items": []}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        
        # Return cached data if available
        if _mls_cache["data"] is not None:
            print(f"⚠️ Using cached data due to network error ({len(_mls_cache['data'])} properties)")
            return {"items": _mls_cache["data"]}
        
        return {"items": []}
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        
        # Return cached data if available
        if _mls_cache["data"] is not None:
            print(f"⚠️ Using cached data due to error ({len(_mls_cache['data'])} properties)")
            return {"items": _mls_cache["data"]}
        
        return {"items": []}


def clear_cache():
    """
    Manually clear the MLS data cache.
    Useful for testing or forcing a refresh.
    """
    global _mls_cache
    _mls_cache["data"] = None
    _mls_cache["timestamp"] = None
    print("✅ MLS cache cleared")


def get_cache_status() -> dict:
    """
    Get current cache status for monitoring.
    """
    global _mls_cache
    
    if _mls_cache["data"] is None:
        return {
            "cached": False,
            "properties": 0,
            "age_seconds": 0
        }
    
    age = time.time() - _mls_cache["timestamp"] if _mls_cache["timestamp"] else 0
    
    return {
        "cached": True,
        "properties": len(_mls_cache["data"]),
        "age_seconds": int(age),
        "age_minutes": int(age / 60),
        "ttl_remaining": int(_mls_cache["ttl"] - age)
    }